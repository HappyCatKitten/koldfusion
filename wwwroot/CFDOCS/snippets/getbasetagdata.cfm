<!--- sn_sysorder.cfm sets ThisTag.ItemCount = 0 in its start mode.
      Each sn_sysitem.cfm does:
        <CFSET Order = GetBaseTagData("CF_SN_SYSORDER")>
        <CFSET Order.ThisTag.ItemCount = Order.ThisTag.ItemCount + Attributes.Qty>
      and shows Order.Attributes.Customer in its row. --->
<CF_SN_SYSORDER CUSTOMER="Ada Lovelace">
  <CF_SN_SYSITEM PRODUCT="56K modem" QTY="1">
  <CF_SN_SYSITEM PRODUCT="Netscape 4.7 CD" QTY="2">
  <CF_SN_SYSITEM PRODUCT="Y2K compliance sticker" QTY="5">
</CF_SN_SYSORDER>
