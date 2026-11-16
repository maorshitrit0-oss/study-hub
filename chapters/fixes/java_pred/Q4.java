public class Q4 {
    static int sum(int[] a) {
        for (int i = 0; i < a.length; i++) {
            int s = 0;
            s += a[i];
        }
        return s;
    }

    public static void main(String[] args) {
        int[] a = {1, 2, 3};
        int r = sum(a);
        double d = 3.5;
        int k = d;
        System.out.println(r + k);
    }
}
