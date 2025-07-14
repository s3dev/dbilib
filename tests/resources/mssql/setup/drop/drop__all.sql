/*
    Purpose:    Deconstruct the testing database.
    Author:     J. Berendt
    Date:       2025-07-14
    Revision:   1

    Updates:
    1:  Written.
*/

DROP VIEW [dbo].[v_guitars_fender];
DROP PROCEDURE [dbo].[usp_get_guitars_colour];
DROP PROCEDURE [dbo].[usp_insert_guitars_add_new];
DROP PROCEDURE [dbo].[usp_insert_players_add_new];
DROP PROCEDURE [dbo].[usp_update_guitars_colour];
DROP TABLE [dbo].[guitars];
DROP TABLE [dbo].[players];
