public class Again {
    public static void main(String[] args) {
        char[] answers = {'y', 'Y', 'n'};
        int k = 0, rounds = 0;
        char again;
        do {
            rounds++;
            again = answers[k++];
        } while (again == 'y' && again == 'Y');
        System.out.println(rounds);
    }
}
