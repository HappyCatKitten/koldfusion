/*
 * Employee - a small Java class for the CFOBJECT examples: public fields, overloaded methods, a static method
 * and a checked exception with extra information (see GetException()).
 *
 *   <CFOBJECT TYPE="Java" ACTION="Create" CLASS="Employee" NAME="emp">
 *   <CFSET emp.init("Ben", "Forta")>
 */
import java.util.Vector;

public class Employee {
    public String firstName = "";
    public String lastName = "";
    public double salary;
    public static int headCount;
    private final Vector skills = new Vector();
    private int grade = 1;

    public Employee() { headCount++; }

    public Employee(String firstName, String lastName) {
        this();
        this.firstName = firstName;
        this.lastName = lastName;
    }

    public String getFullName() { return (firstName + " " + lastName).trim(); }

    /** overloaded on the parameter type: JavaCast("int", ...) picks this one */
    public String setJobGrade(int grade) {
        this.grade = grade;
        return "grade set to number " + grade;
    }

    /** ... and JavaCast("String", ...) this one ("A".."E") */
    public String setJobGrade(String letter) {
        this.grade = "ABCDE".indexOf(letter.toUpperCase()) + 1;
        return "grade set to letter " + letter.toUpperCase() + " (" + this.grade + ")";
    }

    public int getJobGrade() { return grade; }

    public double raise(double percent) throws EmployeeException {
        if (percent < 0 || percent > 50)
            throw new EmployeeException("A raise of " + percent + "% is not allowed", 42);
        salary = salary * (1 + percent / 100);
        return salary;
    }

    public void addSkill(String s) { skills.addElement(s); }

    public Vector getSkills() { return skills; }

    public String[] getNameParts() { return new String[] { firstName, lastName }; }

    public static String company() { return "Gibson Mainframe Co."; }

    public String toString() { return "Employee[" + getFullName() + "]"; }

    /** the exception for GetException(): it carries an error code */
    public static class EmployeeException extends Exception {
        private final int code;
        public EmployeeException(String msg, int code) { super(msg); this.code = code; }
        public int getErrorCode() { return code; }
        public String getErrorMessage() { return getMessage() + " (error " + code + ")"; }
    }
}
