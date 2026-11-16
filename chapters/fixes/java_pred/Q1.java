public class Q1 {
    public static void main(String[] args) {
        int x = 7, y = 2;
        int a = x++ + --y * 3;
        double avg = (x + y) / 2;
        int b = -16 >> 2;
        int c = -16 >>> 28;
        System.out.println(a + " " + avg + " " + b + " " + c);
        System.out.println("" + x + y + (x + y));
    }
}
