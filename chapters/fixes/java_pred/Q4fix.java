public class Q4fix {
    static int sum(int[] a) {
        int s = 0;
        for (int i = 0; i < a.length; i++) {
            s += a[i];
        }
        return s;
    }

    public static void main(String[] args) {
        int[] a = {1, 2, 3};
        int r = sum(a);
        double d = 3.5;
        int k = (int) d;
        System.out.println(r + k);
    }
}
