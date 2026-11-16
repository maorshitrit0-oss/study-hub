public class Q2 {
    static int count = 0;
    int id;

    Q2() {
        count++;
        id = count;
    }

    static void change(int v, int[] arr, Q2 o) {
        v++;
        arr[0]++;
        o.id += 10;
        o = new Q2();
        o.id = 99;
    }

    public static void main(String[] args) {
        int v = 1;
        int[] arr = {1, 2};
        Q2 a = new Q2();
        change(v, arr, a);
        System.out.println(v + " " + arr[0] + " " + a.id + " " + Q2.count);
    }
}
