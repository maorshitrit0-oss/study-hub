public class Q5 {
    public static void main(String[] args) {
        int[] a = {3, -1, 7, 7, 2};
        int m = 0;
        for (int i = 1; i < a.length; i++) {
            if (a[i] > a[m]) {
                m = i;
            }
        }
        System.out.println(m);
        String all = "";
        int sum = 0;
        for (String s : args) {
            all += s;
            sum += Integer.parseInt(s);
        }
        System.out.println(all + " " + sum);
    }
}
