/*
    Purpose:    Deconstruct the testing database.
    Author:     J. Berendt
    Date:       2025-07-25
    Revision:   2

    Updates:
    1:  Written.
    2:  Updated to include dropping the table from the backup database and
        testing the OBJECT_ID before calling DROP.
*/

IF OBJECT_ID('dbilib_test..v_guitars_fender') IS NOT NULL           DROP VIEW [dbo].[v_guitars_fender];
IF OBJECT_ID('dbilib_test..usp_get_guitars_colour') IS NOT NULL     DROP PROCEDURE [dbo].[usp_get_guitars_colour];
IF OBJECT_ID('dbilib_test..usp_insert_guitars_add_new') IS NOT NULL DROP PROCEDURE [dbo].[usp_insert_guitars_add_new];
IF OBJECT_ID('dbilib_test..usp_insert_players_add_new') IS NOT NULL DROP PROCEDURE [dbo].[usp_insert_players_add_new];
IF OBJECT_ID('dbilib_test..usp_update_guitars_colour') IS NOT NULL  DROP PROCEDURE [dbo].[usp_update_guitars_colour];
IF OBJECT_ID('dbilib_test..guitars') IS NOT NULL                    DROP TABLE [dbo].[guitars];
IF OBJECT_ID('dbilib_test..players') IS NOT NULL                    DROP TABLE [dbo].[players];
IF OBJECT_ID('__bak__dbilib_test') IS NOT NULL                      DROP TABLE [__bak__dbilib_test].[dbo].[guitars];

