import java.util.Scanner;

public class Avg {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        int count;
        do {
            count = input.nextInt();
            if (count <= 0) {
                System.out.println("Please enter a positive number.");
            }
        } while (count <= 0);
        double sum = 0;
        for (int i = 1; i <= count; i++) {
            sum += input.nextDouble();
        }
        System.out.println("Sum = " + sum);
        System.out.println("Average = " + sum / count);
    }
}
