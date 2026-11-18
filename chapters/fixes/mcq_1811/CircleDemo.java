class Circle {
    private double radius;
    private String color;
    private static int count = 0;

    Circle(double radius, String color) {
        this.radius = radius;
        this.color = color;
        count++;
    }

    void setRadius(double radius) {
        this.radius = radius;
    }

    double area() {
        return Math.PI * radius * radius;
    }

    static int getCount() {
        return count;
    }
}

public class CircleDemo {
    public static void main(String[] args) {
        Circle a = new Circle(1, "red");
        Circle b = new Circle(2, "blue");
        Circle c = b;
        c.setRadius(3);
        System.out.println(Circle.getCount() + " " + (int) b.area());
    }
}
