public class Q3 {
    public static void main(String[] args) {
        String a = "java";
        String b = new String("java");
        String c = "ja" + "va";
        String d = "ja";
        d = d + "va";
        System.out.println((a == b) + " " + a.equals(b) + " " + (a == c) + " " + (a == d) + " " + a.equals(d));
    }
}
