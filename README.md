# Detection Changed Web Resource

This code provides a REST API which can be called to detect if the content of a website has changed. 
One application scenario is to execute the code using an Azure Function. The Azure Function can then be integrated into a Logic App. The Logic App can be called regularly and can send an e-mail when changes are made to the website.  

This repository is meant to showcase the potential of Azure Functions. It does not contain any production-ready code and is meant to be used in small demo tenants.

## Method
Post-Request

## Required URL Parameters
**url**: URL, which should be monitored by the Azure Function

## Body
Please past the **account_name** and **account_key** in a Json file in the body. 

## Responses
**Code 202**: First time URL has been tested

**Code 201**: URL has changed

**Code 200**: URL has not changed

**Code 204**: Website does not exist anymore

**Code 209**: RequestException was thrown 

**Code 400**: Required parameters url, account_name and account_key were not passed correctly

## Structure of Table Storage
This code uses a table storage as storage type. 

The structure of the storage should look like this: PARTITIONKEY, ROWKEY, TIMESTAMP, HASH, URL










