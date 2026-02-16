# Builder User Manual

The **Builder** is the "Low-Code" heart of FlaskERP. It allows administrators to create, modify, and extend the application's functionalities directly from the web interface, without writing a single line of code.

This guide will walk you through the fundamental steps to use the Builder and create your own custom application.

## 1. Project Management

A **Project** is an isolated container for your applications. Each project has its own models, data, members, and settings.

### Creating a New Project

1.  Navigate to the **Project Selection** page.
2.  If you are an administrator, you will see a **"Create Project"** button. Click it.
3.  Fill out the form:
    -   **Internal Name**: A unique identifier for the project (e.g., `fleet_management`). Use only lowercase letters, numbers, and underscores. **Cannot be changed after creation.**
    -   **Visible Title**: The name that will appear in the interface (e.g., "Company Fleet Management").
    -   **Version**: The initial version of your project (e.g., `1.0.0`).
    -   **Description**: A brief explanation of the project's purpose.
4.  Click **"Create"**. You will be redirected to the new project's dashboard.

### Managing Project Settings

Once inside a project, you can modify its settings:
1.  In the side menu, click on **"Settings"**.
2.  From here you can update the **Title**, **Description**, and **Version**.
3.  At the bottom of the page, in the "Danger Zone", you can **delete the project**. This action is irreversible and will delete all associated models and data.

### Managing Project Members

You can decide which users have access to a project.
1.  In the side menu, click on **"Team Members"**.
2.  You will see the list of users who are part of the project.
3.  To add a new member, click on **"Add Member"**.
    -   If you are an **Admin**, you can select a user from a list.
    -   If you are an **Owner**, you will need to enter the user's numeric ID.
4.  To remove a member, click the trash icon next to their name.

---

## 2. Model Management (Tables)

A **Model** represents a table in the database (e.g., `Vehicles`, `Maintenance`).

### Creating a New Model

1.  Make sure you are in the correct project.
2.  In the side menu, go to **Administration -> Builder**.
3.  Click on **"Create New Model"**.
4.  Select the **Project** to which the model belongs.
5.  Fill in the fields:
    -   **Internal Name**: The name of the table (e.g., `vehicles`).
    -   **Display Title**: The name that will appear in the menu (e.g., `Vehicles`).
6.  Click **Create**.

### Configuring Permissions (ACL)

⚠️ **Fundamental Step**: Without permissions, no one (not even the admin) will be able to see or use the new module.

1.  From the list of models in the Builder, click on **"Manage"** next to your new model.
2.  On the detail page, click on **"Edit Model"**.
3.  In the **Permissions (ACL)** section, check the boxes for the roles that need access.
    -   **Read**: Allows viewing data.
    -   **Write**: Allows creating, modifying, and deleting data.
4.  Click **"Update Model"**.

### Adding Fields to the Model

On the model detail page, you will see the list of fields.
1.  Click on **"Add New Field"**.
2.  Fill out the form:
    -   **Field Name**: Name of the column in the DB (e.g., `license_plate`).
    -   **Field Title**: Label displayed in the form (e.g., `License Plate`).
    -   **Type**: The data type. Choose from `String`, `Integer`, `Date`, `Select`, `Relation`, etc.
    -   **Required/Unique**: Set whether the field is mandatory or must be unique.
3.  Depending on the type, additional options will appear (e.g., options for `Select`, target table for `Relation`).
4.  Save the field.

### Generating the Table in the Database

After defining the fields, you need to create the physical table in the database.
1.  On the model detail page, click the blue **"Generate/Update DB Table"** button.
2.  Confirm the operation.

If you modify the fields in the future (adding, removing, or changing type), you will have to click this button again to synchronize the database schema.

---

## 3. Using the Created Application

Once the table is generated, reload the page (F5). In the side menu, under the **"Applications"** item, your new module will appear. By clicking on it, you will access a complete CRUD page to manage your data.