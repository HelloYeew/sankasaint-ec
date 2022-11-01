# Plan for migrating old flow to new flow

## Overview

The new flow is a complete rewrite from the old flow but we don't want the old system to completely break 
so that's why we need to gradually migrate the old flow to the new flow without clean up all legacy data.

## Migration plan

Note : The migration plan is not final and may change in the future.

Sign :
- 🔴 : Not started
- ✈ : In progress
- 🚀 : Code worked, waiting for deployment
- 🟢 : Done

### 🚀 Migrate and rename all old tables that need to change to legacy tables

Since we need to store all legacy data we need to migrate all old tables that need to change to legacy tables and on the new flow 
we will create a new table that will store the new data.

On a new run, the old database table will rename to `Legacy<name>` without effect the current frontend and API.

### ✈ Make frontend show the legacy data with legacy sign

We will start make some 'sign' on the frontend that this data comes from the old database.

### ✈ Create a new table for the new data

After finish seperate the old data and the new data we will create a new table for the new data with the new schema.

### 🔴 Make frontend show both old and new data

After finish creating the new table we will make the frontend show both old and new data. Except the form that still target to the old table.

### 🔴 Apply change on the form to target to the new table

After finish showing both old and new data we will apply change on the form to target to the new table.

### 🔴 Add / Drop the old view that show the old data

After finish almost all the migration process, we will start remove some view that's show the old data.