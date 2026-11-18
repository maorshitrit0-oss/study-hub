public class Prime {
    static boolean isPrime(int num) {
        if (num <= 1) {
            return false;
        }
        for (int i = 2; i < Math.sqrt(num); i++) {
            if (num % i == 0) {
                return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(9 + (isPrime(9) ? " is prime." : " is not prime."));
        System.out.println(7 + (isPrime(7) ? " is prime." : " is not prime."));
    }
}
