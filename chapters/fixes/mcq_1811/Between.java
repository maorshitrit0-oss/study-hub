public class Between {
    public static void main(String[] args) {
        double a = 2.5, b = -1.2;
        int start = (int) Math.ceil(Math.min(a, b));
        int end = (int) Math.floor(Math.max(a, b));
        for (int i = start; i <= end; i++) {
            System.out.print(i + " ");
        }
        System.out.println();
    }
}
