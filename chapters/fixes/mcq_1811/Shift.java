public class Shift {
    public static void main(String[] args) {
        int b1 = -128;
        int c1 = (b1 >>> 1);
        int d1 = (b1 >> 1);
        System.out.println(c1 + " " + d1);
        int i = 10, j = 3, k = 0;
        k = ++j + i;
        System.out.println(i + " " + j + " " + k);
        int x = 5;
        System.out.println(x++ + ++x);
        System.out.println(x);
        int sum = 7, count = 2;
        System.out.println(sum / count);
        System.out.println((double) sum / count);
        System.out.println((double) (sum / count));
    }
}
