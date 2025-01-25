package com.passwordgenerator;

import java.util.Random;

public class PasswordGenerator {
    public String generatePassword(boolean useLowercase, boolean useUppercase, 
                        boolean useDigits, boolean useSpecialChars, int length) {

        // Define character pools for each type of character
        String lowercaseChars = "abcdefghijklmnopqrstuvwxyz";
        String uppercaseChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        String digits = "0123456789";
        String specialChars = "!@#$%^&*()_+-=[]{}|;:,.<>?/\\";
        
        // Build a pool of valid characters based on user preferences
        StringBuilder validChars = new StringBuilder();
        if (useLowercase) validChars.append(lowercaseChars);
        if (useUppercase) validChars.append(uppercaseChars);
        if (useDigits) validChars.append(digits);
        if (useSpecialChars) validChars.append(specialChars);
        
        // Check if at least one character type is selected
        if (validChars.length() == 0) {
            throw new IllegalArgumentException("At least one character type must be selected.");
        }

        // Generate the password
        StringBuilder password = new StringBuilder();
        Random rand = new Random();

        // Iterate through the length of the checks
        for (int i = 0; i < length; i++) {
            // Randomly select a character from the valid character pool
                // Gen random number to work as index
            int randomindex = rand.nextInt(validChars.length());
                // Take that index and get the character
            char nextChar = validChars.charAt(randomindex); 
            password.append(nextChar);
        }

        return password.toString();
    }        
}
