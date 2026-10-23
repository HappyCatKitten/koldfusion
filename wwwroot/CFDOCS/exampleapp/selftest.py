#!/usr/bin/env python3
"""
selftest.py - walks every page of the KoldFusion Example Applications and
exercises the multi-step flows (login, directory edit, forum posts, cart and
checkout, room booking, HRApp insert/update, CFGRIDUPDATE, ...).

Usage:   python3 wwwroot/CFDOCS/exampleapp/selftest.py [port]     (default 8602)
Start a server first:  ./bin/kfserver -p 8602 &
The tests add rows to the cfexamples and CompanyInfo data sources (and clean
most of them up again). To restore the sample data, stop the server, delete
kfroot/db/cfexamples and kfroot/db/CompanyInfo, and start it again.
"""
import glob, html, http.cookiejar, os, random, re, sys, time, urllib.parse, urllib.request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8602
BASE = 'http://127.0.0.1:%d' % PORT
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SPOOL = os.path.join(ROOT, 'kfroot', 'mail', 'spool')
UNDELIVR = os.path.join(ROOT, 'kfroot', 'mail', 'undelivr')

passed = failed = 0


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


class Browser:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.follow = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.nofollow = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar), NoRedirect)

    def req(self, path, data=None, follow=True):
        if isinstance(data, (dict, list)):
            data = urllib.parse.urlencode(data)
        body = data.encode() if data is not None else None
        opener = self.follow if follow else self.nofollow
        try:
            r = opener.open(BASE + path, body, timeout=30)
            return r.status, r.geturl(), r.read().decode('latin-1')
        except urllib.error.HTTPError as e:
            return e.code, path, e.read().decode('latin-1')

    get = lambda self, p, **k: self.req(p, None, **k)
    post = lambda self, p, d, **k: self.req(p, d, **k)


def check(name, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print('FAIL: %s %s' % (name, detail))


def text(page):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', page)))


def ok_page(name, status, page, *needles):
    err = 'Error Diagnostic Information' in page
    detail = ''
    if err:
        m = re.search(r'Error Diagnostic Information(.{0,400})', text(page))
        detail = m.group(1) if m else ''
    check(name + ' renders', status == 200 and not err, '(HTTP %s) %s' % (status, detail))
    for n in needles:
        check('%s contains %r' % (name, n), n in text(page) or n in page)


def form_fields(page, form_name):
    """the name/value pairs a browser would submit for one form (no checkboxes)"""
    m = re.search(r'<FORM NAME="%s".*?</FORM>' % re.escape(form_name), page, re.S | re.I)
    out = []
    for inp in re.finditer(r'<INPUT ([^>]*)>', m.group(0), re.I):
        a = dict((k.lower(), html.unescape(v1 or v2)) for k, v1, v2 in
                 re.findall(r'(\w+)=(?:"([^"]*)"|([^\s>]*))', inp.group(1)))
        if a.get('type', 'text').lower() in ('checkbox', 'radio', 'submit', 'button', 'reset') or 'name' not in a:
            continue
        out.append((a['name'], a.get('value', '')))
    return out


def spooled_mail_with(subject):
    for d in (SPOOL, UNDELIVR):
        for f in glob.glob(os.path.join(d, '*')):
            try:
                if subject in open(f, encoding='latin-1').read():
                    return True
            except OSError:
                pass
    return False


# ------------------------------------------------------------------ hub
def test_hub():
    b = Browser()
    s, u, p = b.get('/CFDOCS/examplehome.cfm')
    ok_page('examplehome', s, p, 'GlobalCorp Intranet', 'Human Resources Employee Manager',
            'National Parks Finder', 'CFGRID and CFTREE Controls')
    s, u, p = b.get('/CFDOCS/exampleapp/index.cfm', follow=False)
    check('exampleapp/index redirects', s in (301, 302))
    s, u, p = b.get('/CFDOCS/exampleapp/sourcewindow.cfm?file=GlobalCorp/index.cfm')
    ok_page('sourcewindow', s, p, 'Application.cfm', '&lt;CFINCLUDE TEMPLATE=&quot;header.cfm&quot;&gt;')
    for bad in ['../welcome.cfm', '/etc/passwd', 'GlobalCorp/../../welcome.cfm', 'images/gc_logo.gif',
                '..%5C..%5Cwelcome.cfm', 'GlobalCorp//index.cfm']:
        s, u, p = b.get('/CFDOCS/exampleapp/sourcewindow.cfm?file=' + bad)
        check('sourcewindow refuses ' + bad, 'Sorry, only the source' in p and 'CFOUTPUT' not in p)
    s, u, p = b.get('/CFDOCS/exampleapp/sourcewindow.cfm?file=GlobalCorp/nosuch.cfm')
    check('sourcewindow missing file', 'There is no example template' in p)


# ------------------------------------------------------------------ GlobalCorp
GC = '/CFDOCS/exampleapp/GlobalCorp'


def test_globalcorp():
    b = Browser()
    s, u, p = b.get(GC + '/index.cfm')
    ok_page('login form', s, p, 'Please Log In', 'mfeld')
    s, u, p = b.post(GC + '/index.cfm', {'Login_UserName': 'mfeld', 'Login_Password': 'nope'})
    check('bad login refused', 'combination was not found' in p)
    s, u, p = b.post(GC + '/directory/index.cfm', {'Login_UserName': 'guest', 'Login_Password': 'guest'})
    ok_page('guest login lands on requested page', s, p, 'Employee Directory', 'Guest Visitor')
    s, u, p = b.get(GC + '/directory/edit.cfm')
    check('guest cannot edit directory', 'Not Authorized' in p)
    s, u, p = b.get(GC + '/logout.cfm')
    check('logout shows login form', 'Please Log In' in p)

    s, u, p = b.post(GC + '/index.cfm', {'Login_UserName': 'mfeld', 'Login_Password': 'widget'})
    ok_page('home page', s, p, "Here is what's new", 'Company Headlines', 'You are visitor number', 'MARKET')
    check('stock ticker fetched over CFHTTP', 'GLBC' in p and 'Quote server not responding' not in p)
    hits = re.findall(r'digit_(\d)\.gif', p)
    s, u, p2 = b.get(GC + '/index.cfm')
    hits2 = re.findall(r'digit_(\d)\.gif', p2)
    check('hit counter increments', hits and hits2 and int(''.join(hits2)) > int(''.join(hits)))

    s, u, p = b.get(GC + '/quoteserver/quotes.cfm?symbols=GLBC,WDGT')
    check('quote server', s == 200 and len([l for l in p.splitlines() if l.count('|') == 3]) == 2, p[:200])

    # news
    for path in ['/news.cfm', '/news.cfm?ID=1', '/news.cfm?action=new']:
        s, u, p = b.get(GC + path)
        ok_page('news ' + path, s, p)
    headline = 'Selftest headline %d' % random.randint(1000, 9999)
    s, u, p = b.post(GC + '/news.cfm', {'Headline': headline, 'Story': 'Posted by selftest.py'})
    ok_page('post headline', s, p, 'Your headline has been posted', headline)

    test_directory(b)
    test_forum(b)
    test_catalog(b)
    test_scheduler(b)


def test_directory(b):
    D = GC + '/directory'
    for path in ['/index.cfm', '/index.cfm?letter=K', '/index.cfm?Dept_ID=2', '/search.cfm',
                 '/detail.cfm?Emp_ID=24', '/detail.cfm?Emp_ID=99999', '/edit.cfm', '/edit.cfm?Emp_ID=5']:
        s, u, p = b.get(D + path)
        ok_page('directory ' + path, s, p)
    s, u, p = b.get(D + '/index.cfm')
    check('directory grouped by department', p.count('Mail stop') >= 8)
    s, u, p = b.post(D + '/search.cfm', {'DoSearch': 'Yes', 'LastName': 'Ko', 'FirstName': '', 'Title': '', 'Dept_ID': '0'})
    ok_page('directory search', s, p, 'Kowalski, Agnes', 'Kowalczyk, Desmond')
    # server-side validation via hidden fields
    s, u, p = b.post(D + '/save.cfm', {'Emp_ID': '0', 'FirstName': '', 'LastName': 'X', 'StartDate': 'someday',
                                       'Dept_ID': '1', 'FirstName_required': 'First name is required.',
                                       'StartDate_date': 'Start date must be a date.'})
    check('directory server-side validation', 'First name is required.' in p and 'Start date must be a date.' in p)
    # add
    last = 'Testperson%d' % random.randint(1000, 9999)
    fields = {'Emp_ID': '0', 'FirstName': 'Selma', 'LastName': last, 'Title': 'Intern', 'Dept_ID': '7',
              'Email': 'selma@globalcorp.example', 'Phone': '555-0100 x4999', 'Office': 'L-099',
              'StartDate': '06/01/2000', 'Photo': 'photo_3.gif', 'Notes': "Selma's notes",
              'FirstName_required': 'x', 'LastName_required': 'x', 'StartDate_date': 'x', 'SaveButton': 'Add Employee'}
    s, u, p = b.post(D + '/save.cfm', fields)
    ok_page('directory add', s, p, 'has been saved', last, "Selma's notes")
    emp_id = re.search(r'Emp_ID=(\d+)', u).group(1)
    fields.update({'Emp_ID': emp_id, 'Title': 'Junior Developer', 'SaveButton': 'Update Entry'})
    s, u, p = b.post(D + '/save.cfm', fields)
    ok_page('directory update', s, p, 'Junior Developer')
    s, u, p = b.get(D + '/edit.cfm?Emp_ID=' + emp_id)
    check('edit form prefilled', 'VALUE="%s"' % last in p and 'SELECTED' in p)
    fields['DeleteButton'] = 'Delete'
    s, u, p = b.post(D + '/save.cfm', fields)
    s, u, p = b.get(D + '/index.cfm')
    check('directory delete', last not in p)


def test_forum(b):
    F = GC + '/forum'
    for path in ['/index.cfm', '/topic.cfm?Topic_ID=1', '/topic.cfm?Topic_ID=2', '/message.cfm?Msg_ID=1',
                 '/post.cfm?Topic_ID=3', '/post.cfm?Topic_ID=3&ParentID=11']:
        s, u, p = b.get(F + path)
        ok_page('forum ' + path, s, p)
    subj = 'Selftest thread %d' % random.randint(1000, 9999)
    s, u, p = b.post(F + '/post_action.cfm', {'Topic_ID': '5', 'ParentID': '0', 'Author': 'Marcus Feld',
                                              'Email': 'mfeld@globalcorp.example', 'Subject': subj,
                                              'Body': "Anyone want a box of 5.25\" floppies?"})
    ok_page('forum new thread', s, p, 'Your message has been posted', subj, 'floppies')
    root_id = re.search(r'Msg_ID=(\d+)', u).group(1)
    s, u, p = b.post(F + '/post_action.cfm', {'Topic_ID': '5', 'ParentID': root_id, 'Author': 'Tessa Grunwald',
                                              'Email': '', 'Subject': 'Re: ' + subj, 'Body': 'Yes please!'})
    ok_page('forum reply', s, p, 'Re: ' + subj)
    reply_id = re.search(r'Msg_ID=(\d+)', u).group(1)
    check('reply shown in thread tree', 'message.cfm?Msg_ID=%s' % root_id in p)
    s, u, p = b.get(F + '/topic.cfm?Topic_ID=5')
    check('thread shows new GIF', subj in p and 'new.gif' in p)
    check('reply indented under thread', re.search(r'spacer.gif" WIDTH="19".{0,400}Re: ' + re.escape(subj), p, re.S) is not None)


def test_catalog(b):
    C = GC + '/catalog'
    for path in ['/index.cfm', '/category.cfm?Category_ID=1', '/category.cfm?Category_ID=4',
                 '/product.cfm?Product_ID=4', '/cart.cfm', '/orders.cfm']:
        s, u, p = b.get(C + path)
        ok_page('catalog ' + path, s, p)
    s, u, p = b.get(C + '/search.cfm?criteria=widget')
    ok_page('verity search', s, p, 'Model 900 Professional Widget')
    s, u, p = b.get(C + '/search.cfm?criteria=' + urllib.parse.quote('keyboard or mouse'))
    ok_page('verity OR search', s, p, 'Ergonomic Split Keyboard', 'Three-Button Wheel Mouse')
    s, u, p = b.get(C + '/search.cfm?reindex=yes&criteria=cotton')
    ok_page('verity reindex', s, p, 'was just indexed', 'Polo Shirt')
    # cart
    b.get(C + '/cart.cfm?action=empty')
    s, u, p = b.post(C + '/cart.cfm', {'action': 'add', 'Product_ID': '1', 'Qty': '2'})
    ok_page('add to cart', s, p, 'was added to your cart', 'Model 100 Desktop Widget')
    s, u, p = b.post(C + '/cart.cfm', {'action': 'add', 'Product_ID': '15', 'Qty': '1'})
    s, u, p = b.post(C + '/cart.cfm', {'action': 'update', 'Qty_1': '3', 'Qty_15': '2'})
    ok_page('update cart', s, p, '$164.85')          # 3 x 49.95 + 2 x 7.50
    check('cart summary custom tag', '5 items, $164.85' in text(p))
    s, u, p = b.get(C + '/cart.cfm?action=remove&Product_ID=15')
    check('remove from cart', 'Coffee Mug' not in text(p).split('Your Shopping Cart')[-1])
    b.post(C + '/cart.cfm', {'action': 'add', 'Product_ID': '15', 'Qty': '4'})
    s, u, p = b.get(C + '/checkout.cfm')
    ok_page('checkout form', s, p, 'Deliver to', 'mfeld@globalcorp.example')
    s, u, p = b.post(C + '/placeorder.cfm', {'ShipName': 'Marcus Feld', 'Email': 'mfeld@globalcorp.example',
                                             'MailStop': 'L-010', 'Notes': 'Selftest order',
                                             'ShipName_required': 'x', 'Email_required': 'x', 'MailStop_required': 'x'})
    ok_page('place order', s, p, 'Your order number is', '$179.85')
    order = re.search(r'order number is\s*<FONT[^>]*><B>(\d+)', p).group(1)
    time.sleep(0.5)
    check('confirmation mail spooled', spooled_mail_with('Company Store order %s confirmation' % order))
    s, u, p = b.get(C + '/cart.cfm')
    check('cart empty after order', 'Your cart is empty' in p)
    s, u, p = b.get(C + '/orders.cfm')
    ok_page('order history', s, p, 'Order %s' % order)
    s, u, p = b.get(C + '/checkout.cfm', follow=False)
    check('checkout with empty cart redirects', s in (301, 302))


def test_scheduler(b):
    S = GC + '/scheduler'
    for path in ['/index.cfm', '/index.cfm?month=2&year=2000', '/index.cfm?Room_ID=1', '/day.cfm', '/rooms.cfm',
                 '/room.cfm?Room_ID=1', '/book.cfm', '/book.cfm?Room_ID=2&date=12/31/2030']:
        s, u, p = b.get(S + path)
        ok_page('scheduler ' + path, s, p)
    s, u, p = b.get(S + '/index.cfm?month=2&year=2000')
    check('calendar has 29 days in Feb 2000', '>29</B>' in p and '>30</B>' not in p)
    when = time.strftime('%m/%d/%Y', time.localtime(time.time() + 86400 * random.randint(40, 300)))
    room = str(random.randint(1, 5))
    base = {'Room_ID': room, 'MeetingDate': when, 'Purpose': 'Selftest meeting', 'BookedBy': 'Marcus Feld'}
    s, u, p = b.post(S + '/book_action.cfm', dict(base, StartTime='1300', EndTime='1430'))
    ok_page('book a room', s, p, 'Room Booked')
    s, u, p = b.post(S + '/book_action.cfm', dict(base, StartTime='1400', EndTime='1500'))
    ok_page('conflicting booking refused', s, p, 'Room Is Taken', 'Selftest meeting')
    s, u, p = b.post(S + '/book_action.cfm', dict(base, StartTime='1430', EndTime='1500'))
    ok_page('back-to-back booking allowed', s, p, 'Room Booked')
    s, u, p = b.post(S + '/book_action.cfm', dict(base, StartTime='1500', EndTime='1400'))
    check('end before start refused', 'has to end after it starts' in p)
    s, u, p = b.post(S + '/book_action.cfm', dict(base, MeetingDate='01/04/1999', StartTime='900', EndTime='1000'))
    check('past date refused', 'in the past' in p)
    s, u, p = b.get(S + '/day.cfm?date=' + urllib.parse.quote(when))
    ok_page('day view', s, p, 'Selftest meeting')
    for bid in re.findall(r'cancel\.cfm\?Booking_ID=(\d+)', p):
        b.get(S + '/cancel.cfm?Booking_ID=' + bid)
    s, u, p = b.get(S + '/day.cfm?date=' + urllib.parse.quote(when))
    check('bookings cancelled', 'Selftest meeting' not in p)


# ------------------------------------------------------------------ HRApp
def test_hrapp():
    b = Browser()
    H = '/CFDOCS/exampleapp/HRApp'
    for path in ['/EmpList.cfm', '/EmpList.cfm?sort=dept', '/EmpList.cfm?sort=salary', '/SearchForm.cfm',
                 '/InsertForm.cfm', '/UpdateList.cfm', '/UpdateForm.cfm?Employee_ID=1']:
        s, u, p = b.get(H + path)
        ok_page('HRApp ' + path, s, p, 'Human Resources Employee Manager')
    s, u, p = b.get(H + '/index.cfm', follow=False)
    check('HRApp index redirects', s in (301, 302))
    s, u, p = b.get(H + '/InsertForm.cfm')
    check('CFSELECT department list', '<SELECT NAME="Department_ID"' in p and 'Training' in p)
    last = 'Hrtest%d' % random.randint(1000, 9999)
    hidden = {'FirstName_required': 'First name is required.', 'LastName_required': 'Last name is required.',
              'StartDate_required': 'x', 'StartDate_date': 'Start date must be a valid date.',
              'Salary_required': 'x', 'Salary_float': 'Salary must be a number (no dollar sign or commas).'}
    s, u, p = b.post(H + '/InsertAction.cfm', dict(hidden, FirstName='Ida', LastName=last, Department_ID='2',
                                                  StartDate='03/15/2000', Salary='41250', Contract='Yes'))
    ok_page('CFINSERT', s, p, 'has been added')
    s, u, p = b.get(H + '/EmpList.cfm')
    m = re.search(r'Employee_ID=(\d+)">%s, Ida' % last, p)
    check('inserted employee listed', m is not None)
    eid = m.group(1)
    check('inserted values', '$41,250.00' in text(p).split(last)[1][:120])
    s, u, p = b.post(H + '/UpdateAction.cfm', dict(hidden, Employee_ID=eid, FirstName='Ida', LastName=last,
                                                  Department_ID='7', StartDate='04/01/2000', Salary='43000', Contract='No'))
    ok_page('CFUPDATE', s, p, 'has been updated')
    s, u, p = b.get(H + '/UpdateForm.cfm?Employee_ID=' + eid)
    check('updated values', 'VALUE="43000"' in p and 'VALUE="04/01/2000"' in p)
    s, u, p = b.post(H + '/SearchAction.cfm', {'LastName': last[:6], 'Department_ID': '7', 'MinSalary': '42000',
                                               'MaxSalary': '', 'StartedAfter': '01/01/2000', 'Contract': 'No'})
    ok_page('HRApp search', s, p, last)
    s, u, p = b.post(H + '/InsertAction.cfm', dict(hidden, FirstName='', LastName='X', Department_ID='1',
                                                  StartDate='31/31/31', Salary='$1,000', Contract='No'))
    check('HRApp server-side validation', 'First name is required.' in p and 'Start date must be a valid date.' in p
          and 'Salary must be a number' in p)


# ------------------------------------------------------------------ parks
def test_parks():
    b = Browser()
    P = '/CFDOCS/exampleapp/parks'
    s, u, p = b.get(P + '/index.cfm')
    ok_page('parks index', s, p, 'California', 'Wyoming')
    s, u, p = b.get(P + '/parklist.cfm?State=CA')
    ok_page('parks CA page 1', s, p, 'Showing parks 1-5 of 12', 'Next 5')
    s, u, p = b.get(P + '/parklist.cfm?State=CA&StartRow=11')
    ok_page('parks CA page 3', s, p, 'Showing parks 11-12 of 12', 'Previous 5', 'Yosemite')
    check('no Next on last page', 'Next ' not in text(p).split('Page:')[1])
    s, u, p = b.get(P + '/parklist.cfm?Region=Intermountain&StartRow=6')
    ok_page('parks region page', s, p, 'Showing parks 6-10')
    s, u, p = b.get(P + '/parklist.cfm?ParkName=canyon')
    ok_page('parks name search', s, p, 'Grand Canyon')
    s, u, p = b.get(P + '/parklist.cfm?ParkName=zzzz')
    ok_page('parks no match', s, p, 'No parks matched')
    s, u, p = b.get(P + '/parklist.cfm')
    ok_page('parks all', s, p, 'of 71')
    s, u, p = b.get(P + '/detail.cfm?Park_ID=12&State=CA&StartRow=11')
    ok_page('park detail', s, p, 'Yosemite', 'Also in California', 'StartRow=11')


# ------------------------------------------------------------------ widgets
def test_widgets():
    b = Browser()
    W = '/CFDOCS/exampleapp/widgets'
    s, u, p = b.get(W + '/index.cfm')
    ok_page('widgets', s, p, 'CFGRID VendorGrid', 'CFTREE ParkTree', 'CFTREE OrgChart', 'Denali')
    fields = form_fields(p, 'VendorForm')
    d = dict(fields)
    rowname = [k for k, v in d.items() if re.match(r'__CFGRID__VendorGrid__\d+__City$', k)][0]
    newcity = 'Testville%d' % random.randint(100, 999)
    newname = 'Selftest Supply %d' % random.randint(100, 999)
    fields = [(k, newcity if k == rowname else (newname if k == '__CFGRID__VendorGrid__NEW__VendorName' else v))
              for k, v in fields]
    s, u, p = b.post(W + '/gridaction.cfm', fields)
    ok_page('CFGRIDUPDATE update+insert', s, p, 'Your changes were saved', newcity, newname)
    # delete the row we inserted
    fields = form_fields(p, 'VendorForm')
    d = dict(fields)
    row = [re.search(r'__(\d+)__', k).group(1) for k, v in d.items() if v == newname and '__ORIG__' not in k][0]
    fields.append(('__CFGRID__VendorGrid__%s__DELETE' % row, '1'))
    s, u, p = b.post(W + '/gridaction.cfm', fields)
    check('CFGRIDUPDATE delete', newname not in p)
    s, u, p = b.post(W + '/treeaction.cfm', {'ParkTree.node': '/Alaska/AK/Denali', 'WidgetCount': '7'})
    ok_page('tree action', s, p, 'You picked Denali')
    s, u, p = b.get(W + '/gridlink.cfm?CFGRIDKEY=2', follow=False)
    check('grid link redirect', s in (301, 302))


# ------------------------------------------------------------------ every template renders
def test_every_template():
    """any template not exercised above: fetch it (logged in for GlobalCorp) and make sure it has no error"""
    b = Browser()
    b.post(GC + '/index.cfm', {'Login_UserName': 'lybarra', 'Login_Password': 'hr4all'})
    skip = {'logout.cfm', 'loginform.cfm', 'header.cfm', 'footer.cfm', 'toolbar.cfm', 'Application.cfm',
            'threadtree.cfm', 'cartsummary.cfm', 'pricetag.cfm'}
    n = 0
    for f in sorted(glob.glob(os.path.join(HERE, '**', '*.cfm'), recursive=True)):
        rel = os.path.relpath(f, HERE).replace(os.sep, '/')
        if os.path.basename(f) in skip:
            continue
        s, u, p = b.get('/CFDOCS/exampleapp/' + rel)
        ok_page('GET ' + rel, s, p)
        n += 1
        # every template's source can be viewed
        s, u, p = b.get('/CFDOCS/exampleapp/sourcewindow.cfm?file=' + urllib.parse.quote(rel))
        check('source of ' + rel, 'Other templates here' in p and '<PRE>' in p)
    check('templates found', n > 30, str(n))


if __name__ == '__main__':
    random.seed()
    for t in (test_hub, test_globalcorp, test_hrapp, test_parks, test_widgets, test_every_template):
        try:
            t()
        except Exception as e:  # keep going; report the crash as a failure
            failed += 1
            print('FAIL: %s raised %r' % (t.__name__, e))
    print('%d passed, %d failed' % (passed, failed))
    sys.exit(1 if failed else 0)
