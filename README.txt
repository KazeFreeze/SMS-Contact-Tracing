Requirements:
-Android Smartphone with AirMore App (Allow SMS Connectivity and WiFi Connectivity Permissions, Don't Restrict Battery Usage)
-MySQL Database (Import the provided Population Schema)
-Laptop/PC 
-WiFi Host

Setup:
1. Connect the Laptop and Smartphone to the same WiFi Network. 
2. Retrieve the IP Address from the AirMore app on the smartphone.
3. Input the retrieved AirMore IP Address in the secrets.py file.
4. Retrieve the MySQL Database credentials of a user with administrator privileges.
5. Input the retrieved MySQL Database credentials in the secrets.py file.
6. Open the 'run.bat' file to start the contact tracing service.
7. Register a phone number to be set as an administrator for the contact tracing service.
8. Run the MySQL Workbench.
9. Go to the users table in the population schema and change the auth_level of the registered phone number to 3.

The administrator phone number can then give privileges to other users using the contact tracing service itself.


Notes:
-It is advised to connect the smartphone to a local hotspot hosted by the Laptop/PC that is running the service to avoid connection issues.
-Keep the smartphone screen turned on while running the service, this can be enabled in the settings of the AirMore App
-The IP Address of the smartphone resets whenever the WiFI Host restarts so be sure to modify the secrets.py IP accordingly.
-You can delete the pre-existing user on the users table.

Contact me if you need further help:
tapirua@gmail.com


This service is copyrighted (IPOPHL 2021)*
