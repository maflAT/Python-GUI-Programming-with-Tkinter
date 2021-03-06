============================
 ABQ Data Entry Application
============================

Description
===========

This program provides a data entry form for ABQ Agrilabs laboratory data.

Features
--------

* Provides a validated entry form to ensure correct data
* Stores data to ABQ-format CSV files
* Auto-fills form fields whenever possible

Authors
=======

Alan D Moore, 2018
maflAT, 2021

Requirements
============

* Python 3.9
* Tkinter

Usage
=====

To start the application, run::

  py abq_data_entry.py


General Notes
=============

The CSV file will be saved to your current directory in the format
"abq_data_record_CURRENTDATE.csv", where CURRENTDATE is today's date in ISO format.

This program only appends to the CSV file. You should have a spreadsheet program
installed in case you need to edit or check the file.
