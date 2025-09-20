/*
    Purpose:    Primary database and user creation script.
    Author:     J. Berendt
    Date:       2023-05-17
    Revision:   1

    Note:       This script must be run by the root user account.

    Updates:
    1:  Written.
*/

-- DROP/CREATE DATABASE
-- DROP DATABASE `dblib_test`;
CREATE DATABASE `dbilib_test`;

-- CREATE LOCAL USERS FOR BOTH DATABASES
-- CREATE USER 'testuser'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'testing123';
CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'testing123';

-- GRANT ADMIN/SELECT PRIVILEGES FOR THESE DATABASES
GRANT ALL PRIVILEGES ON `dbilib_test`.* TO 'testuser'@'localhost';

-- RESET AND PICK UP NEW PRIVILEGES
FLUSH PRIVILEGES;

