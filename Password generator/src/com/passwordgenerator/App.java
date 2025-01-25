package com.passwordgenerator;

import java.util.Scanner;

public class App {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Welcome to the Password Generator!");

        // Get user preferences
        System.out.print("Include lowercase letters? (true/false): ");
        boolean useLowercase = scanner.nextBoolean();

        System.out.print("Include uppercase letters? (true/false): ");
        boolean useUppercase = scanner.nextBoolean();

        System.out.print("Include digits? (true/false): ");
        boolean useDigits = scanner.nextBoolean();

        System.out.print("Include special characters? (true/false): ");
        boolean useSpecialChars = scanner.nextBoolean();

        // Validate password length
        int length = 0;
        while (length <= 0) {
            System.out.print("Enter the length of the password (must be greater than 0): ");
            length = scanner.nextInt();
            if (length <= 0) {
                System.out.println("Invalid length. Please enter a positive integer.");
            }
        }

        scanner.close();

        // Generate and display the password
        PasswordGenerator passwordGen = new PasswordGenerator();
        String password = passwordGen.generatePassword(useLowercase, useUppercase, useDigits, useSpecialChars, length);
        System.out.println("Generated Password: " + password);
    }
}