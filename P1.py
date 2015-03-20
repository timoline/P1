#!python3
# P1 Datalogger
# Release 0.73 / M401 / Iskra / S0 / pv / pvo
# Author J. van der Linde
# Copyright (c) 2011/2012/2013/2014 J. van der Linde
#
# Although there is a explicit copyright on this sourcecode, anyone may use it freely under a 
# "Creative Commons Naamsvermelding-NietCommercieel-GeenAfgeleideWerken 3.0 Nederland" licentie.
# Please check http://creativecommons.org/licenses/by-nc-nd/3.0/nl/ for details
#
# This software is provided as is and comes with absolutely no warranty.
# The author is not responsible or liable (direct or indirect) to anyone for the use or misuse of this software.
# Any person using this software does so entirely at his/her own risk. 
# That person bears sole responsibility and liability for any claims or actions, legal or civil, arising from such use.
# If you believe this software is in breach of anyone's copyright you will inform the author immediately so the offending material 
# can be removed upon receipt of proof of copyright for that material.
#
# Dependend on Python 3.x and Python 3.x packages: PySerial 2.5
#

progname='P1.py'
version = "v0.73"
import_db = False
import sys
import serial
import datetime
import csv
import json
import os
import locale
import socket
socket.setdefaulttimeout(30)
import http.client
import urllib.parse
MySQL_loaded = True
try:
    import mysql.connector
except ImportError:
    MySQL_loaded=False
from time import sleep
import argparse
#####################################################################
# pvoutput.org system parameters
#####################################################################
pvo_url = 'http://pvoutput.org/service/r2/addstatus.jsp'
#####################################################################

class P1_ChannelData:
    def __init__(self, id=0, type_id=0, type_desc='', equipment_id='', timestamp='0000-00-00 00:00:00', meterreading=0.0, unit='', valveposition=0):
        self.id = id
        self.type_id = type_id
        self.type_desc = type_desc
        self.equipment_id = equipment_id
        self.timestamp = timestamp
        self.meterreading = meterreading
        self.unit = unit
        self.valveposition = valveposition

def scan_serial():
#  scan for available ports. return a list of tuples (num, name)
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            if win_os:
# Windows style COM portname is returned from serial: COM1, COM2, etc...            
                available.append( (i, s.portstr))
            else:
# Linux Style COM portname is not correctly returned, should be /dev/ttyUSB0, /dev/ttyUSB1, etc...            
                available.append( (i, "/dev/ttyUSB"+str(i) ) )
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available
    
################
#Error display #
################
def show_error():
    ft = sys.exc_info()[0]
    fv = sys.exc_info()[1]
    print("Fout type: %s" % ft )
    print("Fout waarde: %s" % fv )
    return
    
################
#Scherm output #
################
def print_p1_telegram():
    print ("---------------------------------------------------------------------------------------")
    print ("P1 telegram ontvangen op: %s" % p1_timestamp)
    if p1_meter_supplier == "KMP":
        print ("Meter fabrikant: Kamstrup")
    elif p1_meter_supplier == "ISk":
        print ("Meter fabrikant: IskraEmeco")
    elif p1_meter_supplier == "XMX":
        print ("Meter fabrikant: Xemex")
    elif p1_meter_supplier == "KFM":
        print ("Meter fabrikant: Kaifa")
    else:
        print ("Meter fabrikant: Niet herkend")
    print ("Meter informatie: %s" % p1_header )
    print (" 0. 2. 8 - DSMR versie: %s" % p1_dsmr_version )
    print ("96. 1. 1 - Meternummer Elektriciteit: %s" % p1_equipment_id )
    print (" 1. 8. 1 - Meterstand Elektriciteit levering (T1/Laagtarief): %0.3f %s" % (p1_meterreading_in_1,p1_unitmeterreading_in_1) )
    print (" 1. 8. 2 - Meterstand Elektriciteit levering (T2/Normaaltarief): %0.3f %s" % (p1_meterreading_in_2,p1_unitmeterreading_in_2) )
    print (" 2. 8. 1 - Meterstand Elektriciteit teruglevering (T1/Laagtarief): %0.3f %s" % (p1_meterreading_out_1,p1_unitmeterreading_out_1) )
    print (" 2. 8. 2 - Meterstand Elektriciteit teruglevering (T2/Normaaltarief): %0.3f %s" % (p1_meterreading_out_2,p1_unitmeterreading_out_2) )
    print ("96.14. 0 - Actueel tarief Elektriciteit: %d" % p1_current_tariff )
    print (" 1. 7. 0 - Actueel vermogen Electriciteit levering (+P): %0.3f %s" % (p1_current_power_in,p1_unit_current_power_in) )
    print (" 2. 7. 0 - Actueel vermogen Electriciteit teruglevering (-P): %0.3f %s" % (p1_current_power_out,p1_unit_current_power_out) )
    print ("17. 0. 0 - Actuele doorlaatwaarde Elektriciteit: %0.3f %s" % (p1_current_threshold,p1_unit_current_threshold) )
    print ("96. 3.10 - Actuele schakelaarpositie Elektriciteit: %s" % p1_current_switch_position )
    print ("96. 7.21 - Aantal onderbrekingen Elektriciteit: %s" % p1_powerfailures )
    print ("96. 7. 9 - Aantal lange onderbrekingen Elektriciteit: %s" % p1_long_powerfailures )
    print ("99.97. 0 - Lange onderbrekingen Elektriciteit logboek: %s" % p1_long_powerfailures_log )
    print ("32.32. 0 - Aantal korte spanningsdalingen Elektriciteit in fase 1: %s" % p1_voltage_sags_l1 )
    print ("52.32. 0 - Aantal korte spanningsdalingen Elektriciteit in fase 2: %s" % p1_voltage_sags_l2 )
    print ("72.32. 0 - Aantal korte spanningsdalingen Elektriciteit in fase 3: %s" % p1_voltage_sags_l3 )
    print ("32.36. 0 - Aantal korte spanningsstijgingen Elektriciteit in fase 1: %s" % p1_voltage_swells_l1 )
    print ("52.36. 0 - Aantal korte spanningsstijgingen Elektriciteit in fase 2: %s" % p1_voltage_swells_l2 )
    print ("72.36. 0 - Aantal korte spanningsstijgingen Elektriciteit in fase 3: %s" % p1_voltage_swells_l3 )       
    print ("31. 7. 0 - Instantane stroom Elektriciteit in fase 1: %0.3f %s" % (p1_instantaneous_current_l1,p1_unit_instantaneous_current_l1) )  
    print ("51. 7. 0 - Instantane stroom Elektriciteit in fase 2: %0.3f %s" % (p1_instantaneous_current_l2,p1_unit_instantaneous_current_l2) )  
    print ("71. 7. 0 - Instantane stroom Elektriciteit in fase 3: %0.3f %s" % (p1_instantaneous_current_l3,p1_unit_instantaneous_current_l3) )     
    print ("32. 7. 0 - Spanning Elektriciteit in fase 1: %0.3f %s" % (p1_voltage_l1,p1_unit_voltage_l1) )  
    print ("52. 7. 0 - Spanning Elektriciteit in fase 2: %0.3f %s" % (p1_voltage_l2,p1_unit_voltage_l2) )  
    print ("72. 7. 0 - Spanning Elektriciteit in fase 3: %0.3f %s" % (p1_voltage_l3,p1_unit_voltage_l3) )  
    print ("21. 7. 0 - Instantaan vermogen Elektriciteit levering (+P) in fase 1: %0.3f %s" % (p1_instantaneous_active_power_in_l1,p1_unit_instantaneous_active_power_in_l1) )  
    print ("41. 7. 0 - Instantaan vermogen Elektriciteit levering (+P) in fase 2: %0.3f %s" % (p1_instantaneous_active_power_in_l2,p1_unit_instantaneous_active_power_in_l2) )  
    print ("61. 7. 0 - Instantaan vermogen Elektriciteit levering (+P) in fase 3: %0.3f %s" % (p1_instantaneous_active_power_in_l3,p1_unit_instantaneous_active_power_in_l3) )   
    print ("22. 7. 0 - Instantaan vermogen Elektriciteit teruglevering (-P) in fase 1: %0.3f %s" % (p1_instantaneous_active_power_out_l1,p1_unit_instantaneous_active_power_out_l1) )  
    print ("42. 7. 0 - Instantaan vermogen Elektriciteit teruglevering (-P) in fase 2: %0.3f %s" % (p1_instantaneous_active_power_out_l2,p1_unit_instantaneous_active_power_out_l2) )  
    print ("62. 7. 0 - Instantaan vermogen Elektriciteit teruglevering (-P) in fase 3: %0.3f %s" % (p1_instantaneous_active_power_out_l3,p1_unit_instantaneous_active_power_out_l3) )   
    print ("96.13. 1 - Bericht code: %s" % p1_message_code )
    print ("96.13. 0 - Bericht tekst: %s" % p1_message_text )
    channellist = [p1_channel_1, p1_channel_2, p1_channel_3, p1_channel_4]
    for channel in channellist:
        if channel.id != 0:
            print ("MBus Meterkanaal: %s" % channel.id )
            print ("24. 1. 0 - Productsoort: %s (%s)" % (channel.type_id, channel.type_desc) )
            print ("91. 1. 0 - Meternummer %s: %s" % (channel.type_desc, channel.equipment_id) )
            if p1_dsmr_version != "40":
                print ("24. 3. 0 - Tijdstip meterstand %s levering: %s" % (channel.type_desc, channel.timestamp) )
                print ("24. 3. 0 - Meterstand %s levering: %0.3f %s" % (channel.type_desc, channel.meterreading, channel.unit) )
            else:
                print ("24. 2. 1 - Tijdstip meterstand %s levering: %s" % (channel.type_desc, channel.timestamp) )
                print ("24. 2. 1 - Meterstand %s levering: %0.3f %s" % (channel.type_desc, channel.meterreading, channel.unit) )            
            print ("24. 4. 0 - Actuele kleppositie %s: %s" % (channel.type_desc,channel.valveposition) )
    print ("Einde P1 telegram" )
    return
################
#Csv output #
################
def csv_p1_telegram():
#New filename every day
    csv_filename=datetime.datetime.strftime(datetime.datetime.today(), "P1_"+"%Y-%m-%d_"+str(log_interval*10)+"s.csv" )
    try:
#If csv_file exists: open it
        csv_file=open(csv_filename, 'rt')
        csv_file.close()
        csv_file=open(csv_filename, 'at', newline='', encoding="utf-8")
        writer = csv.writer(csv_file, dialect='excel', delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
    except IOError:
#Otherwise: create it
        csv_file=open(csv_filename, 'wt', newline='', encoding="utf-8")
        writer = csv.writer(csv_file, dialect='excel', delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
#Write csv-header
        writer.writerow([
         'p1_timestamp', 
         'p1_meter_supplier', 
         'p1_header',
         'p1_dsmr_version',
         'p1_equipment_id', 
         'p1_meterreading_in_1', 
         'p1_unitmeterreading_in_1', 
         'p1_meterreading_in_2', 
         'p1_unitmeterreading_in_2',
         'p1_meterreading_out_1',
         'p1_unitmeterreading_out_1',
         'p1_meterreading_out_2',
         'p1_unitmeterreading_out_2',
         'p1_current_tariff',
         'p1_current_power_in',
         'p1_unit_current_power_in',
         'p1_current_power_out',
         'p1_unit_current_power_out',
         'p1_current_threshold',
         'p1_unit_current_threshold',
         'p1_current_switch_position',
         'p1_powerfailures',
         'p1_long_powerfailures',
         'p1_long_powerfailures_log',
         'p1_voltage_sags_l1',
         'p1_voltage_sags_l2',
         'p1_voltage_sags_l3',
         'p1_voltage_swells_l1',
         'p1_voltage_swells_l2',
         'p1_voltage_swells_l3',
         'p1_instantaneous_current_l1',
         'p1_unit_instantaneous_current_l1',
         'p1_instantaneous_current_l2',
         'p1_unit_instantaneous_current_l2',
         'p1_instantaneous_current_l3',
         'p1_unit_instantaneous_current_l3',
         'p1_voltage_l1',
         'p1_unit_voltage_l1',
         'p1_voltage_l2',
         'p1_unit_voltage_l2',
         'p1_voltage_l3',
         'p1_unit_voltage_l3',             
         'p1_instantaneous_active_power_in_l1',
         'p1_unit_instantaneous_active_power_in_l1',
         'p1_instantaneous_active_power_in_l2',
         'p1_unit_instantaneous_active_power_in_l2',
         'p1_instantaneous_active_power_in_l3',
         'p1_unit_instantaneous_active_power_in_l3',
         'p1_instantaneous_active_power_out_l1',
         'p1_unit_instantaneous_active_power_out_l1',
         'p1_instantaneous_active_power_out_l2',
         'p1_unit_instantaneous_active_power_out_l2',
         'p1_instantaneous_active_power_out_l3',
         'p1_unit_instantaneous_active_power_out_l3',
         'p1_message_code',
         'p1_message_text',
         'p1_channel_1_id',
         'p1_channel_1_type_id', 
         'p1_channel_1_type_desc',
         'p1_channel_1_equipment_id',
         'p1_channel_1_timestamp',
         'p1_channel_1_meterreading', 
         'p1_channel_1_unit',
         'p1_channel_1_valveposition',
         'p1_channel_2_id',
         'p1_channel_2_type_id', 
         'p1_channel_2_type_desc',
         'p1_channel_2_equipment_id',
         'p1_channel_2_timestamp',
         'p1_channel_2_meterreading', 
         'p1_channel_2_unit',
         'p1_channel_2_valveposition',
         'p1_channel_3_id',
         'p1_channel_3_type_id', 
         'p1_channel_3_type_desc',
         'p1_channel_3_equipment_id',
         'p1_channel_3_timestamp',
         'p1_channel_3_meterreading', 
         'p1_channel_3_unit',
         'p1_channel_3_valveposition',
         'p1_channel_4_id',
         'p1_channel_4_type_id', 
         'p1_channel_4_type_desc',
         'p1_channel_4_equipment_id',
         'p1_channel_4_timestamp',
         'p1_channel_4_meterreading', 
         'p1_channel_4_unit',
         'p1_channel_4_valveposition' ])

    print ("P1 telegram in %s gelogd op: %s" % (csv_filename, p1_timestamp) )
    writer.writerow([
         p1_timestamp, 
         p1_meter_supplier, 
         p1_header, 
         p1_dsmr_version,    
         p1_equipment_id,
         p1_meterreading_in_1, p1_unitmeterreading_in_1, 
         p1_meterreading_in_2, p1_unitmeterreading_in_2,
         p1_meterreading_out_1,p1_unitmeterreading_out_1,
         p1_meterreading_out_2,p1_unitmeterreading_out_2,
         p1_current_tariff,
         p1_current_power_in,p1_unit_current_power_in,
         p1_current_power_out,p1_unit_current_power_out,
         p1_current_threshold,p1_unit_current_threshold,
         p1_current_switch_position,
         p1_powerfailures,
         p1_long_powerfailures,
         p1_long_powerfailures_log,
         p1_voltage_sags_l1,
         p1_voltage_sags_l2,
         p1_voltage_sags_l3,
         p1_voltage_swells_l1,
         p1_voltage_swells_l2,
         p1_voltage_swells_l3,
         p1_instantaneous_current_l1, p1_unit_instantaneous_current_l1,
         p1_instantaneous_current_l2, p1_unit_instantaneous_current_l2,
         p1_instantaneous_current_l3, p1_unit_instantaneous_current_l3,
         p1_voltage_l1, p1_unit_voltage_l1,
         p1_voltage_l2, p1_unit_voltage_l2,
         p1_voltage_l3, p1_unit_voltage_l3,   
         p1_instantaneous_active_power_in_l1, p1_unit_instantaneous_active_power_in_l1,
         p1_instantaneous_active_power_in_l2, p1_unit_instantaneous_active_power_in_l2,
         p1_instantaneous_active_power_in_l3, p1_unit_instantaneous_active_power_in_l3,
         p1_instantaneous_active_power_out_l1, p1_unit_instantaneous_active_power_out_l1,
         p1_instantaneous_active_power_out_l2, p1_unit_instantaneous_active_power_out_l2,
         p1_instantaneous_active_power_out_l3, p1_unit_instantaneous_active_power_out_l3,
         p1_message_code,
         p1_message_text,
         p1_channel_1.id,
         p1_channel_1.type_id, 
         p1_channel_1.type_desc,
         p1_channel_1.equipment_id,
         p1_channel_1.timestamp,
         p1_channel_1.meterreading, p1_channel_1.unit,
         p1_channel_1.valveposition,
         p1_channel_2.id,
         p1_channel_2.type_id, 
         p1_channel_2.type_desc,
         p1_channel_2.equipment_id,
         p1_channel_2.timestamp,
         p1_channel_2.meterreading, p1_channel_2.unit,
         p1_channel_2.valveposition,
         p1_channel_3.id,
         p1_channel_3.type_id, 
         p1_channel_3.type_desc,
         p1_channel_3.equipment_id,
         p1_channel_3.timestamp,
         p1_channel_3.meterreading, p1_channel_3.unit,
         p1_channel_3.valveposition,
         p1_channel_4.id,
         p1_channel_4.type_id, 
         p1_channel_4.type_desc,
         p1_channel_4.equipment_id,
         p1_channel_4.timestamp,
         p1_channel_4.meterreading, p1_channel_4.unit,
         p1_channel_4.valveposition ])
    csv_file.close()
    
    return        

################
#json output #
################
def json_p1_telegram():

	data = {
		'p1_timestamp' : p1_timestamp,
		'p1_meter_supplier' : p1_meter_supplier,
		'p1_header': p1_header,
		'p1_dsmr_version' : p1_dsmr_version,
		'p1_equipment_id' : p1_equipment_id, 
		'p1_meterreading_in_1' : p1_meterreading_in_1,
		'p1_unitmeterreading_in_1' : p1_unitmeterreading_in_1,
		'p1_meterreading_in_2' : p1_meterreading_in_2,
		'p1_unitmeterreading_in_2' : p1_unitmeterreading_in_2,
		'p1_meterreading_out_1' : p1_meterreading_out_1,
		'p1_unitmeterreading_out_1' : p1_unitmeterreading_out_1,
		'p1_meterreading_out_2' : p1_meterreading_out_2,
		'p1_unitmeterreading_out_2' : p1_unitmeterreading_out_2,
		'p1_current_tariff' : p1_current_tariff,
		'p1_current_power_in' : p1_current_power_in,
		'p1_unit_current_power_in' : p1_unit_current_power_in,
		'p1_current_power_out' : p1_current_power_out,
		'p1_unit_current_power_out' : p1_unit_current_power_out,
		'p1_current_threshold' : p1_current_threshold,
		'p1_unit_current_threshold' : p1_unit_current_threshold,
		'p1_current_switch_position' : p1_current_switch_position,
		'p1_powerfailures' : p1_powerfailures,
		'p1_long_powerfailures' : p1_long_powerfailures,
		'p1_long_powerfailures_log' : p1_long_powerfailures_log,
		'p1_voltage_sags_l1' : p1_voltage_sags_l1,
		'p1_voltage_sags_l2' : p1_voltage_sags_l2,
		'p1_voltage_sags_l3' : p1_voltage_sags_l3,
		'p1_voltage_swells_l1' : p1_voltage_swells_l1,
		'p1_voltage_swells_l2' : p1_voltage_swells_l2,
		'p1_voltage_swells_l3' : p1_voltage_swells_l3,
		'p1_instantaneous_current_l1' : p1_instantaneous_current_l1,
		'p1_unit_instantaneous_current_l1' : p1_unit_instantaneous_current_l1,
		'p1_instantaneous_current_l2' : p1_instantaneous_current_l2,
		'p1_unit_instantaneous_current_l2' : p1_unit_instantaneous_current_l2,
		'p1_instantaneous_current_l3' : p1_instantaneous_current_l3,
		'p1_unit_instantaneous_current_l3' : p1_unit_instantaneous_current_l3,
		'p1_voltage_l1' : p1_voltage_l1,
		'p1_unit_voltage_l1' : p1_unit_voltage_l1,
		'p1_voltage_l2' : p1_voltage_l2,
		'p1_unit_voltage_l2' : p1_unit_voltage_l2,
		'p1_voltage_l3' : p1_voltage_l3,
		'p1_unit_voltage_l3' : p1_unit_voltage_l3,
		'p1_instantaneous_active_power_in_l1' : p1_instantaneous_active_power_in_l1,
		'p1_unit_instantaneous_active_power_in_l1' :  p1_unit_instantaneous_active_power_in_l1,
		'p1_instantaneous_active_power_in_l2' : p1_instantaneous_active_power_in_l2,
		'p1_unit_instantaneous_active_power_in_l2' : p1_unit_instantaneous_active_power_in_l2,
		'p1_instantaneous_active_power_in_l3' : p1_instantaneous_active_power_in_l3,
		'p1_unit_instantaneous_active_power_in_l3' : p1_unit_instantaneous_active_power_in_l3,
		'p1_instantaneous_active_power_out_l1' : p1_instantaneous_active_power_out_l1,
		'p1_unit_instantaneous_active_power_out_l1' : p1_unit_instantaneous_active_power_out_l1,
		'p1_instantaneous_active_power_out_l2' : p1_instantaneous_active_power_out_l2,
		'p1_unit_instantaneous_active_power_out_l2' : p1_unit_instantaneous_active_power_out_l2,
		'p1_instantaneous_active_power_out_l3' : p1_instantaneous_active_power_out_l3,
		'p1_unit_instantaneous_active_power_out_l3' : p1_unit_instantaneous_active_power_out_l3,
		'p1_message_code' : p1_message_code,
		'p1_message_text' : p1_message_text,
		'p1_channel_1_id' : p1_channel_1.id,
		'p1_channel_1_type_id' : p1_channel_1.type_id,
		'p1_channel_1_type_desc' : p1_channel_1.type_desc,
		'p1_channel_1_equipment_id' : p1_channel_1.equipment_id,
		'p1_channel_1_timestamp' : p1_channel_1.timestamp,
		'p1_channel_1_meterreading' : p1_channel_1.meterreading,
		'p1_channel_1_unit' : p1_channel_1.unit,
		'p1_channel_1_valveposition' : p1_channel_1.valveposition,
		'p1_channel_2_id' : p1_channel_2.id,
		'p1_channel_2_type_id' : p1_channel_2.type_id,
		'p1_channel_2_type_desc' : p1_channel_2.type_desc,
		'p1_channel_2_equipment_id' : p1_channel_2.equipment_id,
		'p1_channel_2_timestamp' : p1_channel_2.timestamp,
		'p1_channel_2_meterreading' : p1_channel_2.meterreading,
		'p1_channel_2_unit' : p1_channel_2.unit,
		'p1_channel_2_valveposition' : p1_channel_2.valveposition,
		'p1_channel_3_id' : p1_channel_3.id,
		'p1_channel_3_type_id' : p1_channel_3.type_id,
		'p1_channel_3_type_desc' : p1_channel_3.type_desc,
		'p1_channel_3_equipment_id' : p1_channel_3.equipment_id,
		'p1_channel_3_timestamp' : p1_channel_3.timestamp,
		'p1_channel_3_meterreading' : p1_channel_3.meterreading,
		'p1_channel_3_unit' : p1_channel_3.unit,
		'p1_channel_3_valveposition' : p1_channel_3.valveposition,
		'p1_channel_4_id' : p1_channel_4.id,
		'p1_channel_4_type_id' : p1_channel_4.type_id,
		'p1_channel_4_type_desc' : p1_channel_4.type_desc,
		'p1_channel_4_equipment_id' : p1_channel_4.equipment_id,
		'p1_channel_4_timestamp' : p1_channel_4.timestamp,
		'p1_channel_4_meterreading' : p1_channel_4.meterreading,
		'p1_channel_4_unit' : p1_channel_4.unit,
		'p1_channel_4_valveposition' : p1_channel_4.valveposition
	}

	json_str = json.dumps(data)

# Writing JSON data
	json_filename='p1data.json'
	with open(json_filename, 'w') as f:
	 json.dump(data, f, sort_keys=True) # indent=4 Prettify format
 
	print ("P1 telegram in %s gelogd op: %s" % (json_filename, p1_timestamp) )

	return      
    
################
#DB output     #
################
def db_p1_telegram():
    query = "insert into p1_log values (\'" + \
         p1_timestamp + "\',\'" + \
         p1_meter_supplier + "\',\'" + \
         p1_header + "\',\'" + \
         p1_dsmr_version + "\',\'" + \
         p1_equipment_id + "\',\'" + \
         str(p1_meterreading_in_1) + "\',\'" + \
         p1_unitmeterreading_in_1 + "\',\'" + \
         str(p1_meterreading_in_2) + "\',\'" + \
         p1_unitmeterreading_in_2 + "\',\'" + \
         str(p1_meterreading_out_1) + "\',\'" +\
         p1_unitmeterreading_out_1 + "\',\'" + \
         str(p1_meterreading_out_2) + "\',\'" + \
         p1_unitmeterreading_out_2 + "\',\'" + \
         str(p1_current_tariff) + "\',\'" + \
         str(p1_current_power_in) + "\',\'" + \
         p1_unit_current_power_in + "\',\'" + \
         str(p1_current_power_out) + "\',\'" + \
         p1_unit_current_power_out + "\',\'" + \
         str(p1_current_threshold) + "\',\'" + \
         p1_unit_current_threshold + "\',\'" + \
         p1_current_switch_position + "\',\'" + \
         str(p1_powerfailures) + "\',\'" + \
         str(p1_long_powerfailures) + "\',\'" + \
         p1_long_powerfailures_log + "\',\'" + \
         str(p1_voltage_sags_l1)  + "\',\'" + \
         str(p1_voltage_sags_l2) + "\',\'" + \
         str(p1_voltage_sags_l3) + "\',\'" + \
         str(p1_voltage_swells_l1) + "\',\'" + \
         str(p1_voltage_swells_l2) + "\',\'" + \
         str(p1_voltage_swells_l3) + "\',\'" + \
         str(p1_instantaneous_current_l1)  + "\',\'" + \
         p1_unit_instantaneous_current_l1 + "\',\'" + \
         str(p1_instantaneous_current_l2)  + "\',\'" + \
         p1_unit_instantaneous_current_l2 + "\',\'" + \
         str(p1_instantaneous_current_l3)  + "\',\'" + \
         p1_unit_instantaneous_current_l3 + "\',\'" + \
         str(p1_voltage_l1) + "\',\'" + \
         p1_unit_voltage_l1 + "\',\'" + \
         str(p1_voltage_l2) + "\',\'" + \
         p1_unit_voltage_l2 + "\',\'" + \
         str(p1_voltage_l3) + "\',\'" + \
         p1_unit_voltage_l3 + "\',\'" + \
         str(p1_instantaneous_active_power_in_l1)  + "\',\'" + \
         p1_unit_instantaneous_active_power_in_l1 + "\',\'" + \
         str(p1_instantaneous_active_power_in_l2)  + "\',\'" + \
         p1_unit_instantaneous_active_power_in_l2 + "\',\'" + \
         str(p1_instantaneous_active_power_in_l3)  + "\',\'" + \
         p1_unit_instantaneous_active_power_in_l3 + "\',\'" + \
         str(p1_instantaneous_active_power_out_l1)  + "\',\'" + \
         p1_unit_instantaneous_active_power_out_l1 + "\',\'" + \
         str(p1_instantaneous_active_power_out_l2)  + "\',\'" + \
         p1_unit_instantaneous_active_power_out_l2 + "\',\'" + \
         str(p1_instantaneous_active_power_out_l3)  + "\',\'" + \
         p1_unit_instantaneous_active_power_out_l3 + "\',\'" + \
         p1_message_code + "\',\'" + \
         p1_message_text + "\',\'" + \
         str(p1_channel_1.id) + "\',\'" + \
         str(p1_channel_1.type_id) + "\',\'" +  \
         p1_channel_1.type_desc + "\',\'" + \
         str(p1_channel_1.equipment_id) + "\',\'" + \
         p1_channel_1.timestamp + "\',\'" + \
         str(p1_channel_1.meterreading) + "\',\'" + \
         p1_channel_1.unit + "\',\'" + \
         str(p1_channel_1.valveposition) + "\',\'" + \
         str(p1_channel_2.id) + "\',\'" + \
         str(p1_channel_2.type_id) + "\',\'" +  \
         p1_channel_2.type_desc + "\',\'" + \
         str(p1_channel_2.equipment_id) + "\',\'" + \
         p1_channel_2.timestamp + "\',\'" + \
         str(p1_channel_2.meterreading) + "\',\'" + \
         p1_channel_2.unit + "\',\'" + \
         str(p1_channel_2.valveposition) + "\',\'" + \
         str(p1_channel_3.id) + "\',\'" + \
         str(p1_channel_3.type_id) + "\',\'" + \
         p1_channel_3.type_desc + "\',\'" + \
         str(p1_channel_3.equipment_id) + "\',\'" + \
         p1_channel_3.timestamp + "\',\'" + \
         str(p1_channel_3.meterreading) + "\',\'" + \
         p1_channel_3.unit + "\',\'" + \
         str(p1_channel_3.valveposition) + "\',\'" + \
         str(p1_channel_4.id) + "\',\'" + \
         str(p1_channel_4.type_id) + "\',\'" + \
         p1_channel_4.type_desc + "\',\'" + \
         str(p1_channel_4.equipment_id) + "\',\'" + \
         p1_channel_4.timestamp + "\',\'" + \
         str(p1_channel_4.meterreading) + "\',\'" + \
         p1_channel_4.unit + "\',\'" + \
         str(p1_channel_4.valveposition)  + "\')"
#    print(query)
    try:
        db = mysql.connector.connect(user=p1_mysql_user, password=p1_mysql_passwd, host=p1_mysql_host, database=p1_mysql_db)
        c = db.cursor()
        c.execute (query)
        db.commit()
        print ("P1 telegram in database %s / %s gelogd op: %s" % (p1_mysql_host, p1_mysql_db, p1_timestamp) )
        c.close()
        db.close()
    except:
        show_error()
        print ("Fout bij het openen van / schrijven naar database %s / %s. P1 Telegram wordt gelogd in csv-bestand."  % (p1_mysql_host, p1_mysql_db))      
        csv_p1_telegram()
    return    

######################
#PVOutput.org output #
######################
def pvo_p1_telegram():
    global pvo_prev_date
    global p1_prev_meterreading_out_1, p1_prev_meterreading_out_2
    global p1_prev_meterreading_in_1, p1_prev_meterreading_in_2    
    if pvo_url[0:7] != "http://":
        print("Invalid PVOutput.org URL to post to, must be of form http://host/service: %s" % pvo_url)
        sys.exit(1)
    url = pvo_url[7:].split('/')
    pvo_host = url[0]
    pvo_service = '/' + '/'.join(url[1:])
#
# d Date
# t Time
# v1 energy generation (Wh) => P1 Export
# v2 power generation (W) => P1 Export
# v3 energy consumption (Wh) => P1 Import
# v4 power consumption (W) => P1 Import
# v5 temperature (c)
# v6 voltage (V)
# c1 cumulative flag: if set to '1' lifetime values are to be passed
# n  net flag: if set to '1' net import/export values are to be passed
#
    pvo_date=str(datetime.datetime.strftime(datetime.datetime.strptime(p1_timestamp, "%Y-%m-%d %H:%M:%S" ), "%Y%m%d" ))
    pvo_time=str(datetime.datetime.strftime(datetime.datetime.strptime(p1_timestamp, "%Y-%m-%d %H:%M:%S" ), "%H:%M" ))
    
# Initialize pvo volumes when a new day has started
    if pvo_prev_date != pvo_date:
        print ("PVOutput volumes worden gereset, vorige datum: %s, huidige datum: %s" % (pvo_prev_date, pvo_date) )
        p1_prev_meterreading_out_1 = p1_meterreading_out_1
        p1_prev_meterreading_out_2 = p1_meterreading_out_2
        p1_prev_meterreading_in_1 = p1_meterreading_in_1
        p1_prev_meterreading_in_2 = p1_meterreading_in_2
        pvo_prev_date = pvo_date
        
    pvo_volume_out=round((p1_meterreading_out_1+p1_meterreading_out_2-p1_prev_meterreading_out_1-p1_prev_meterreading_out_2) * 1000)
    pvo_volume_in=round((p1_meterreading_in_1+p1_meterreading_in_2-p1_prev_meterreading_in_1-p1_prev_meterreading_in_2) *1000)
    
    pvo_power_out=round(p1_current_power_out * 1000)
    pvo_power_in=round(p1_current_power_in * 1000)
    
    print("PVOutput volume out (v1): %s"% pvo_volume_out)
    print("MR1 out: %s"% p1_meterreading_out_1)
    print("MR2 out: %s"% p1_meterreading_out_2)
    print("Prev MR1 out: %s"% p1_prev_meterreading_out_1)
    print("Prev MR2 out: %s"% p1_prev_meterreading_out_2)

    print("PVOutput volume in (v3): %s"% pvo_volume_in)
    print("MR1 in: %s"% p1_meterreading_in_1)
    print("MR2 in: %s"% p1_meterreading_in_2)
    print("Prev MR1 in: %s"% p1_prev_meterreading_in_1)
    print("Prev MR2 in: %s"% p1_prev_meterreading_in_2)
       

    pvo_cumulative = 0 # volumes are reset once a day
    pvo_net = 0 #Typically not correct but the best you can get with this PVOutput interface as net=1 discards the volume data
    params = urllib.parse.urlencode({ 'd' : pvo_date,
                         't' : pvo_time,
# This is how it should be                         
#                         'v1' : pvo_volume_out,
#                         'v2' : pvo_power_out,
#                         'v3' : pvo_volume_in,
#                         'v4' : pvo_power_in,
# Patch wrong behaviour of PVOutput in case of using net values because PVOutput obly uses power values in this case
                         'v1' : pvo_volume_out,
                         'v2' : pvo_power_out,
                         'v3' : pvo_volume_in,
                         'v4' : pvo_power_in,                         
                         'c1' : pvo_cumulative,
                         'n'  : pvo_net })
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain",
               "X-Pvoutput-SystemId" : pvo_systemid,
               "X-Pvoutput-Apikey" : pvo_apikey}
    print("Verbinden met %s" % pvo_host)
    try:
        conn = http.client.HTTPConnection(pvo_host)
#        print("Sending data: %s" % params)
        try:
            conn.request("POST", pvo_service, params, headers)
            response = conn.getresponse()
            if response.status != 200:
                print ("Fout bij het schrijven naar %s / %s. Response: %s %s %s" % (pvo_host, pvo_systemid, response.status, response.reason, response.read()))
            else: 
                print ("Delta P1 telegram in %s / %s gelogd op: %s. Response: %s %s" % (pvo_host, pvo_systemid, p1_timestamp,response.status, response.reason) )
        except:
            show_error()
            print ("Fout bij het schrijven naar %s / %s."  % (pvo_host, pvo_systemid))      
    except:
        show_error()
        print ("Fout bij het verbinden met %s / %s."  % (pvo_host, pvo_systemid))      
            
#################################################################
# Start of procedures to add other metering data to p1_telegram #
#################################################################

#################################################################
# PV Inverter Data                                              #
#################################################################
def get_pv_data(channelA,p1_channelA,channelB,p1_channelB):
    query = "select pv_timestamp, pv_equipmentmodel, pv_equipmentid, pv_cumvolume, pv_cumvolumeunit, pv_intvolume, pv_intvolumeunit, pv_power, pv_powerunit from pv_log order by pv_timestamp desc"
#    print(query)
    try:
        db = mysql.connector.connect(user=p1_mysql_user, password=p1_mysql_passwd, host=p1_mysql_host, database=p1_mysql_db)
        c = db.cursor()
        c.execute(query)
        pv_timestamp, pv_equipmentmodel, pv_equipmentid, pv_cumvolume, pv_cumvolumeunit, pv_intvolume, pv_intvolumeunit, pv_power, pv_powerunit = c.fetchone()
        p1_channelA.id = channelA
        p1_channelA.type_id = 1
        p1_channelA.type_desc = "E-Production volume"
        p1_channelA.equipment_id = pv_equipmentid
        p1_channelA.timestamp = str(datetime.datetime.strftime(pv_timestamp, "%Y-%m-%d %H:%M:%S" ))
        p1_channelA.meterreading = pv_cumvolume
        p1_channelA.unit = pv_cumvolumeunit
        p1_channelA.valveposition = 1
        print ("PV volume %s toegevoegd aan P1 telegram - kanaal %s" % (pv_timestamp, channelA ) )
        if channelB != 0:
            p1_channelB.id = channelB
            p1_channelB.type_id = 1
            p1_channelB.type_desc = "E-Production power"
            p1_channelB.equipment_id = pv_equipmentid
            p1_channelB.timestamp = str(datetime.datetime.strftime(pv_timestamp, "%Y-%m-%d %H:%M:%S" ))
            p1_channelB.meterreading = pv_power
            p1_channelB.unit = pv_powerunit
            p1_channelB.valveposition = 1
            print ("PV vermogen %s toegevoegd aan P1 telegram - kanaal %s" % (pv_timestamp, channelB ) )
        #c.close()
        db.close()
    except:
        show_error()
        print ("Fout bij het openen / lezen van database %s / %s. PV telegram niet opgehaald."  % (p1_mysql_host, p1_mysql_db))      

    return
#################################################################
# Heat Data                                                     #
#################################################################
def get_heat_data(channelA,p1_channelA,channelB,p1_channelB):
    query = "select heat_timestamp, heat_equipment_id, heat_meterreading_energy, heat_unitmeterreading_energy, heat_meterreading_volume, heat_unitmeterreading_volume from heat_log order by heat_timestamp desc"
#    print(query)
    try:
        db = mysql.connector.connect(user=p1_mysql_user, password=p1_mysql_passwd, host=p1_mysql_host, database=p1_mysql_db)
        c = db.cursor()
        c.execute(query)
        heat_timestamp, heat_equipment_id, heat_meterreading_energy, heat_unitmeterreading_energy, heat_meterreading_volume, heat_unitmeterreading_volume = c.fetchone()
        p1_channelA.id = channelA
        p1_channelA.type_id = 5
        p1_channelA.type_desc = "Heat energy"
        p1_channelA.equipment_id = heat_equipment_id
        p1_channelA.timestamp = str(datetime.datetime.strftime(heat_timestamp, "%Y-%m-%d %H:%M:%S" ))
        p1_channelA.meterreading = heat_meterreading_energy
        p1_channelA.unit = heat_unitmeterreading_energy
        p1_channelA.valveposition = 1
        print ("Warmte energie %s toegevoegd aan P1 telegram - kanaal %s" % (heat_timestamp, channelA ) )
        if channelB != 0:
            p1_channelB.id = channelB
            p1_channelB.type_id = 5
            p1_channelB.type_desc = "Heat flow"
            p1_channelB.equipment_id = heat_equipment_id
            p1_channelB.timestamp = str(datetime.datetime.strftime(heat_timestamp, "%Y-%m-%d %H:%M:%S" ))
            p1_channelB.meterreading = heat_meterreading_volume
            p1_channelB.unit = heat_unitmeterreading_volume
            p1_channelB.valveposition = 1
            print ("Warmte flow %s toegevoegd aan P1 telegram - kanaal %s" % (heat_timestamp, channelB ) )
        #c.close()
        db.close()
    except:
        show_error()
        print ("Fout bij het openen / lezen van database %s / %s. Heat telegram niet opgehaald."  % (p1_mysql_host, p1_mysql_db))      
    return
#################################################################
# S0 Pulse Counter Data                                         #
#################################################################
def get_s0_data(id,meter,channel,p1_channel,type_id,type_desc):
# Use the total s0 volume to improve performance. In the S0 Datalogger, make sure it is not reset!!
    query = "select s0_timestamp, s0_id, s0_m" + meter + "_volume_total, s0_m" + meter + "_volume_total_unit from s0_log where s0_id = '" + id + "' order by s0_timestamp desc limit 1"
#    print(query)
    try:
        db = mysql.connector.connect(user=p1_mysql_user, password=p1_mysql_passwd, host=p1_mysql_host, database=p1_mysql_db)
        c = db.cursor()
        c.execute(query)
        s0_timestamp, s0_id, s0_volume_total, s0_volume_total_unit = c.fetchone()
        p1_channel.id = channel
        p1_channel.type_id = type_id
        p1_channel.type_desc = type_desc
        p1_channel.equipment_id = s0_id  + "-" + meter
        p1_channel.timestamp = str(datetime.datetime.strftime(s0_timestamp, "%Y-%m-%d %H:%M:%S" ))
        p1_channel.meterreading = s0_volume_total
        p1_channel.unit = s0_volume_total_unit
        p1_channel.valveposition = "1"
        print ("S0 %s %s toegevoegd aan P1 telegram - kanaal %s" % (type_desc, s0_timestamp,channel))
        #c.close()
        db.close()
    except:
        show_error()
        print ("Fout bij het openen / lezen van database %s / %s. S0 telegram niet opgehaald."  % (p1_mysql_host, p1_mysql_db))
    return
#################################################################
# Electricity sub-meter                                         #
#################################################################
def get_power_data(channel,p1_channel,type_id,type_desc):
    query = "select power_timestamp, power_equipment_id, power_meterreading_1_tot, power_unitmeterreading_1_tot from power_log order by power_timestamp desc"
#    print(query)
    try:
        db = mysql.connector.connect(user=p1_mysql_user, password=p1_mysql_passwd, host=p1_mysql_host, database=p1_mysql_db)
        c = db.cursor()
        c.execute(query)
        power_timestamp, power_equipment_id, power_meterreading_1_tot, power_unitmeterreading_1_tot = c.fetchone()
        p1_channel.id = channel
        p1_channel.type_id = type_id
        p1_channel.type_desc = type_desc
        p1_channel.equipment_id = row.power_equipment_id
        p1_channel.timestamp = str(row.power_timestamp)
        p1_channel.meterreading = power_meterreading_1_tot
        p1_channel.unit = power_unitmeterreading_1_tot
        p1_channel.valveposition = "1"
        print ("Elektra %s %s toegevoegd aan P1 telegram - kanaal %s" % (type_desc, power_timestamp,channel) )
        #c.close()
        db.close()
    except:
        show_error()
        print ("Fout bij het openen / lezen van database %s / %s. Iskra telegram niet opgehaald."  % (p1_mysql_host, p1_mysql_db))      

    return
#################################################################
# End of procedures to add other metering data to p1_telegram   #
#################################################################    
    
################################################################################################################################################
#Main program
################################################################################################################################################
print("%s %s" % (progname, version))
comport=-1
win_os = (os.name == 'nt')
if win_os:
    print("Windows Mode")
else:
    print("Non-Windows Mode")
print("Python version %s.%s.%s" % sys.version_info[:3])
print ("Control-C to abort")

################################################################################################################################################
#Commandline arguments parsing
################################################################################################################################################    
parser = argparse.ArgumentParser(prog=progname, description='P1 Datalogger - www.smartmeterdashboard.nl', epilog="Copyright (c) 2011/2012/2013/2014 J. van der Linde. Although there is a explicit copyright on this sourcecode, anyone may use it freely under a 'Creative Commons Naamsvermelding-NietCommercieel-GeenAfgeleideWerken 3.0 Nederland' license.")
parser.add_argument("-c", "--comport", help="COM-port identifier", type=int)
parser.add_argument("-l", "--loginterval", help="Log frequency in 10 second-units, default=1", default=1, type=int)
parser.add_argument("-o", "--output", help="Output mode, default='screen'", default='screen', choices=['screen', 'csv', 'db', 'json'])
parser.add_argument("-pvo", "--pvoutput", help="Output to PVOutput ==EXPERIMENTAL==, default='N'", default='N', choices=['Y', 'N'])
parser.add_argument("-pvoapi", "--pvoutputapikey", help="PVOutput.org API key")
parser.add_argument("-pvosys", "--pvoutputsystemid", help="PVOutput.org system id", type=int)
parser.add_argument("-s", "--server", help="Database server, default='localhost'", default='localhost')
parser.add_argument("-u", "--user", help="Database user, default='root'", default='root')
parser.add_argument("-p", "--password", help="Database user password, default='password'", default='password')
parser.add_argument("-d", "--database", help="Database name, default=p1'", default='p1')
parser.add_argument("-v", "--version", help="DSMR COM-port setting version, default=3'", choices=['2','3','4'], default='3')
args = parser.parse_args()

if args.comport == None:
    parser.print_help()
    print ("\r")
    print("%s: error: The following arguments are required: -c/--comport." % progname)
    print("Allowed values for argument -c/--comport:") 
    #scanserial returns win_os serial ports and non win_os USB serial ports
    for n,s in scan_serial():
        port=n+1
        print ("%d --> %s" % (port,s) )
    print ("Program aborted.")
    sys.exit()

comport = args.comport
pvo_output = (args.pvoutput == "Y")
log_interval = args.loginterval
if pvo_output and (args.pvoutputapikey == None or args.pvoutputsystemid == None):
    parser.print_help()
    print ("\r")
    print("%s: error: If -pvo/--pvoutput is 'Y', the following arguments are required: -pvoapi/--pvoutputapikey and -pvosys/--pvoutputsystemid." % progname)
    print ("Program aborted.")
    sys.exit()

if pvo_output and log_interval < 6:
    log_interval = 6
    print("%s: warning: If -pvo/--pvoutput is 'Y', log interval should be 6 or higher. Log interval 6 used instead." % progname)
output_mode = args.output
dsmr_version = args.version
pvo_apikey = args.pvoutputapikey
pvo_systemid = args.pvoutputsystemid
pvo_prev_date = ""

#Show startup arguments
print ("\r")
print ("Startup parameters:")
print ("Output mode           : %s" % output_mode)
print ("PVOutput.org logging  : %s" % pvo_output)
if pvo_output:
    print ("PVOutput.org API key  : %s" % pvo_apikey)
    print ("PVOutput.org system ID: %s" % pvo_systemid)
print ("Log interval          : %s (once every %s seconds)" % (log_interval, log_interval * 10))
print ("DSMR COM-port setting : %s" % dsmr_version)
if (output_mode == "db" or import_db) and MySQL_loaded:
    p1_mysql_host=args.server
    p1_mysql_user=args.user
    p1_mysql_passwd=args.password
    p1_mysql_db=args.database   
    print ("Database credentials used:")
    print ("- Server  : %s" % p1_mysql_host)
    print ("- User    : %s" % p1_mysql_user)
    print ("- Password: %s" % p1_mysql_passwd)
    print ("- Database: %s" % p1_mysql_db)
if (output_mode == "db" or import_db) and not MySQL_loaded:
   print("%s: warning: MySQL Connector/Python not found. Output mode 'db' not allowed. Output mode 'csv' used instead." % progname)
   output_mode = "csv"
   import_db = False   
#################################################################################################################################################
        
#Set COM port config
if comport != 0:
    ser = serial.Serial()
    if dsmr_version == '2' or dsmr_version == '3':
        ser.baudrate = 9600
        ser.bytesize=serial.SEVENBITS
        ser.parity=serial.PARITY_EVEN
        ser.stopbits=serial.STOPBITS_ONE
        ser.xonxoff=1
    if dsmr_version == '4':
        ser.baudrate = 115200
        ser.bytesize=serial.EIGHTBITS
        ser.parity=serial.PARITY_NONE
        ser.stopbits=serial.STOPBITS_ONE
        ser.xonxoff=1
    ser.rtscts=0
    ser.timeout=20
    if win_os:
        ser.port=comport-1
        print ("COM-port              : %d (%s)" % (comport, ser.name) )   
    else:
        ser.port="/dev/ttyUSB"+str(comport-1)
        port="/dev/ttyUSB"+str(comport-1)  # Linux Style for /dev/ttyUSB0, /dev/ttyUSB1, etc...
        print ("COM-port              : %d (%s)" % (comport, port) )
else:
    print ("Inputfile assigned    : 'p1test.log'")

#Open COM port
if comport != 0:
    try:
        ser.open()
    except:
        if win_os:
            sys.exit ("Error opening %s. Program aborted."  % ser.name)
        else:
            sys.exit ("Error opening %s. Program aborted."  %  port) 
else:
    try:
        ser = open("p1test.log", "rt")   
    except:
        sys.exit ("Error opening 'p1test.log'. Program aborted.")      


#Initialize
p1_telegram=False
p1_meter_supplier=""
p1_timestamp=""
p1_dsmr_version="30"
p1_powerfailures=0
p1_long_powerfailures=0
p1_long_powerfailures_log=""
p1_voltage_sags_l1=0
p1_voltage_sags_l2=0
p1_voltage_sags_l3=0
p1_voltage_swells_l1=0
p1_voltage_swells_l2=0
p1_voltage_swells_l3=0
p1_instantaneous_current_l1=0
p1_unit_instantaneous_current_l1=""
p1_instantaneous_current_l2=0
p1_unit_instantaneous_current_l2=""
p1_instantaneous_current_l3=0
p1_unit_instantaneous_current_l3=""
p1_instantaneous_active_power_in_l1=0
p1_unit_instantaneous_active_power_in_l1=""
p1_instantaneous_active_power_in_l2=0
p1_unit_instantaneous_active_power_in_l2=""
p1_instantaneous_active_power_in_l3=0
p1_unit_instantaneous_active_power_in_l3=""
p1_instantaneous_active_power_out_l1=0
p1_unit_instantaneous_active_power_out_l1=""
p1_instantaneous_active_power_out_l2=0
p1_unit_instantaneous_active_power_out_l2=""
p1_instantaneous_active_power_out_l3=0
p1_unit_instantaneous_active_power_out_l3=""
p1_voltage_l1=0
p1_unit_voltage_l1=""
p1_voltage_l2=0
p1_unit_voltage_l2=""
p1_voltage_l3=0
p1_unit_voltage_l3=""
p1_prev_meterreading_out_1 = 0
p1_prev_meterreading_out_2 = 0
p1_prev_meterreading_in_1 = 0
p1_prev_meterreading_in_2 = 0
pvo_volume_initialize = False
pvo_prev_date=""

p1_teller=0

while 1:
    p1_line=''
#Read 1 line
    try:
        p1_raw = ser.readline()
    except:
        if comport != 0:
            if win_os:
                sys.exit ("Error reading %s. Program aborted."  % ser.name)
            else:
               sys.exit ("Error reading %s. Program aborted."  %  port) 
            ser.close()
        else:
            sys.exit ("Error reading 'p1test.log'. Program aborted.")                  
            ser.close()
    if comport == 0 and len(p1_raw) == 0:
            ser.close()  
            sys.exit ("Finished reading 'p1test.log'. Program ended.")                  
    p1_str=p1_raw
    if comport != 0:
        p1_str=str(p1_raw, "utf-8")
    p1_line=p1_str.strip()
    
#Inspect 1st character
    if p1_line[0:1] == "/":
#Start of new P1 telegram
        p1_telegram=True
        p1_teller=p1_teller+1
#P1 Timestamp to cover DSMR 3 and before       
        p1_timestamp=datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S" )
#Initialize P1 channeldata
        p1_channel_1=P1_ChannelData()
        p1_channel_2=P1_ChannelData()
        p1_channel_3=P1_ChannelData()
        p1_channel_4=P1_ChannelData()
        
#Only proceed if P1 telegram start is recognized.        
    if p1_telegram:
        if p1_line[0:1] == "/":
#Header information 
#eg. /KMP5 KA6U001511209910 (Kamstrup Enexis)
#eg. /ISk5\2ME382-1003 (InkraEmeco Liander)
#eg. /XMX5XMXABCE000018914 (Landis&Gyr Stedin, Xemex communicatiemodule)
#eg. /KFM5KAIFA-METER (Kaifa)
            p1_meter_supplier=p1_line[1:4]
            p1_header=p1_line
    
        elif p1_line[4:9] == "1.0.0":
#P1 Timestamp (DSMR 4)
#eg. 0-0:1.0.0(101209113020W)
            if p1_line[10:23] != "000101010000W":
#Check if meter clock is running
                p1_timestamp="20"+p1_line[10:12]+"-"+p1_line[12:14]+"-"+p1_line[14:16]+" "+p1_line[16:18]+":"+p1_line[18:20]+":"+p1_line[20:22]
            else:
                print ("%s: warning: invalid P1-telegram date/time value '%s', system date/time used instead: '%s'" % (progname, p1_line[10:23], p1_timestamp) )

        elif p1_line[4:9] == "0.2.8":
#DSMR Version (DSMR V4)
#eg. 1-3:0.2.8(40)
            p1_lastpos=len(p1_line)-1
            p1_dsmr_version=p1_line[10:p1_lastpos]
            
        elif p1_line[4:10] == "96.1.1":
#####
#Channel 0 = E
#####
#Equipment identifier (Electricity)
#eg. 0-0:96.1.1(204B413655303031353131323039393130)
            p1_lastpos=len(p1_line)-1
            p1_equipment_id=p1_line[11:p1_lastpos]
            
        elif p1_line[4:9] == "1.8.1":
#Meter Reading electricity delivered to client (normal tariff)
#eg. 1-0:1.8.1(00721.000*kWh) (DSMR 3)
#eg. 1-0:1.8.1(000038.851*kWh) (DSMR 4)
#        p1_meterreading_in_1=float(p1_line[10:19])
#        p1_unitmeterreading_in_1=p1_line[20:23]
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_meterreading_in_1=float(p1_line[p1_num_start:p1_num_end])        
            p1_unitmeterreading_in_1=p1_line[p1_num_end+1:p1_lastpos]
        elif p1_line[4:9] == "1.8.2":
#Meter Reading electricity delivered to client (low tariff)
#eg. 1-0:1.8.2(00392.000*kWh)
#        p1_meterreading_in_2=float(p1_line[10:19])
#        p1_unitmeterreading_in_2=p1_line[20:23]
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_meterreading_in_2=float(p1_line[p1_num_start:p1_num_end])        
            p1_unitmeterreading_in_2=p1_line[p1_num_end+1:p1_lastpos]
        elif p1_line[4:9] == "2.8.1":
#Meter Reading electricity delivered by client (normal tariff)
#eg. 1-0:2.8.1(00000.000*kWh)
#        p1_meterreading_out_1=float(p1_line[10:19])
#        p1_unitmeterreading_out_1=p1_line[20:23]
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_meterreading_out_1=float(p1_line[p1_num_start:p1_num_end])        
            p1_unitmeterreading_out_1=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:9] == "2.8.2":
#Meter Reading electricity delivered by client (low tariff)
#eg. 1-0:2.8.2(00000.000*kWh)
#        p1_meterreading_out_2=float(p1_line[10:19])
#        p1_unitmeterreading_out_2=p1_line[20:23]
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_meterreading_out_2=float(p1_line[p1_num_start:p1_num_end])        
            p1_unitmeterreading_out_2=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:11] == "96.14.0":
#Tariff indicator electricity
#eg. 0-0:96.14.0(0001)
#alternative 0-0:96.14.0(1)
            p1_lastpos=len(p1_line)-1
            p1_current_tariff=int(p1_line[12:p1_lastpos])

        elif p1_line[4:9] == "1.7.0":
#Actual electricity power delivered to client (+P)
#eg. 1-0:1.7.0(0000.91*kW)
#        p1_current_power_in=float(p1_line[10:17])
#        p1_unit_current_power_in=p1_line[18:20]
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_current_power_in=float(p1_line[p1_num_start:p1_num_end])        
            p1_unit_current_power_in=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:9] == "2.7.0":
#Actual electricity power delivered by client (-P)
#1-0:2.7.0(0000.00*kW)
#        p1_current_power_out=float(p1_line[10:17])
#        p1_unit_current_power_out=p1_line[18:20]
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_current_power_out=float(p1_line[p1_num_start:p1_num_end])        
            p1_unit_current_power_out=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:10] == "17.0.0":
#Actual threshold Electricity
#Companion standard, eg Kamstrup, Xemex
#eg. 0-0:17.0.0(999*A)
#Iskraemeco
#eg. 0-0:17.0.0(0999.00*kW)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_current_threshold=float(p1_line[p1_num_start:p1_num_end])        
            p1_unit_current_threshold=p1_line[p1_num_end+1:p1_lastpos]
                 
        elif p1_line[4:11] == "96.3.10":
#Actual switch position Electricity (in/out/enabled).
#eg. 0-0:96.3.10(1)
            p1_current_switch_position=p1_line[12:13]

        elif p1_line[4:11] == "96.7.21":
#Number of powerfailures in any phase (DSMR4)
#eg. 0-0:96.7.21(00004)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_powerfailures=int(float(p1_line[p1_num_start:p1_lastpos]))
        
        elif p1_line[4:10] == "96.7.9":
#Number of long powerfailures in any phase (DSMR4)
#eg. 0-0:96.7.9(00002)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_long_powerfailures=int(float(p1_line[p1_num_start:p1_lastpos]))
        
        elif p1_line[4:11] == "99.97.0":
#Powerfailure eventlog (DSMR4)
#eg. 1-0:99:97.0(2)(0:96.7.19)(101208152415W)(0000000240*s)(101208151004W)(00000000301*s)
#    1-0:99.97.0(0)(0-0:96.7.19)
            p1_lastpos=len(p1_line)
            p1_log_start= p1_line.find("0:96.7.19") +10
            p1_long_powerfailures_log=p1_line[p1_log_start:p1_lastpos]
        
        elif p1_line[4:11] == "32.32.0":
#Number of Voltage sags L1 (DSMR4)
#eg. 1-0:32.32.0(00002)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_voltage_sags_l1=int(float(p1_line[p1_num_start:p1_lastpos]))

        elif p1_line[4:11] == "52.32.0":
#Number of Voltage sags L2 (DSMR4)
#eg. 1-0:52.32.0(00002)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_voltage_sags_l2=int(float(p1_line[p1_num_start:p1_lastpos]))

        elif p1_line[4:11] == "72.32.0":
#Number of Voltage sags L3 (DSMR4)
#eg. 1-0:72.32.0(00002)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_voltage_sags_l3=int(float(p1_line[p1_num_start:p1_lastpos]))
        
        elif p1_line[4:11] == "32.36.0":
#Number of Voltage swells L1 (DSMR4)
#eg. 1-0:32.36.0(00002)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_voltage_swells_l1=int(float(p1_line[p1_num_start:p1_lastpos]))

        elif p1_line[4:11] == "52.36.0":
#Number of Voltage swells L2 (DSMR4)
#eg. 1-0:52.36.0(00002)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_voltage_swells_l2=int(float(p1_line[p1_num_start:p1_lastpos]))

        elif p1_line[4:11] == "72.36.0":
#Number of Voltage swells L3 (DSMR4)
#eg. 1-0:72.36.0(00002)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_voltage_swells_l3=int(float(p1_line[p1_num_start:p1_lastpos]))


        elif p1_line[4:10] == "31.7.0":
#Instantaneous current L1 in A (DSMR4)
#eg. 1-0:31.7.0.255(001*A)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_current_l1=int(float(p1_line[p1_num_start:p1_num_end]))
            p1_unit_instantaneous_current_l1=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:10] == "51.7.0":
#Instantaneous current L2 in A (DSMR4)
#eg. 1-0:51.7.0.255(002*A)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_current_l2=int(float(p1_line[p1_num_start:p1_num_end]))
            p1_unit_instantaneous_current_l2=p1_line[p1_num_end+1:p1_lastpos]


        elif p1_line[4:10] == "71.7.0":
#Instantaneous current L3 in A (DSMR4)
#eg. 1-0:71.7.0.255(003*A)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_current_l3=int(float(p1_line[p1_num_start:p1_num_end]))
            p1_unit_instantaneous_current_l3=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:10] == "21.7.0":
#Instantaneous active power L1 (+P) in W (DSMR4)          
#eg 1-0:21.7.0.255(01.111*kW)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_active_power_in_l1=float(p1_line[p1_num_start:p1_num_end])
            p1_unit_instantaneous_active_power_in_l1=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:10] == "41.7.0":
#Instantaneous active power L2 (+P) in W (DSMR4)           
#eg 1-0:41.7.0.255(02.222*kW)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_active_power_in_l2=float(p1_line[p1_num_start:p1_num_end])
            p1_unit_instantaneous_active_power_in_l2=p1_line[p1_num_end+1:p1_lastpos]            

        elif p1_line[4:10] == "61.7.0":
#Instantaneous active power L3 (+P) in W (DSMR4)           
#eg 1-0:61.7.0.255(03.333*kW)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_active_power_in_l3=float(p1_line[p1_num_start:p1_num_end])
            p1_unit_instantaneous_active_power_in_l3=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:10] == "22.7.0":
#Instantaneous active power L1 (+P) in W  (DSMR4)          
#eg 1-0:22.7.0.255(04.444*kW)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_active_power_out_l1=float(p1_line[p1_num_start:p1_num_end])
            p1_unit_instantaneous_active_power_out_l1=p1_line[p1_num_end+1:p1_lastpos]

        elif p1_line[4:10] == "42.7.0":
#Instantaneous active power L2 (+P) in W  (DSMR4)          
#eg 1-0:42.7.0.255(05.555*kW)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_active_power_out_l2=float(p1_line[p1_num_start:p1_num_end])
            p1_unit_instantaneous_active_power_out_l2=p1_line[p1_num_end+1:p1_lastpos]            

        elif p1_line[4:10] == "62.7.0":
#Instantaneous active power L3 (+P) in W (DSMR4)           
#eg 1-0:62.7.0.255(06.666*kW)
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_instantaneous_active_power_out_l3=float(p1_line[p1_num_start:p1_num_end])
            p1_unit_instantaneous_active_power_out_l3=p1_line[p1_num_end+1:p1_lastpos]    

        elif p1_line[4:10] == "32.7.0":
#Voltage level L1 in V (DSMR4)            
#1-0:32.7.0(00234*V) 
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_voltage_l1=int(float(p1_line[p1_num_start:p1_num_end]))
            p1_unit_voltage_l1=p1_line[p1_num_end+1:p1_lastpos]   

        elif p1_line[4:10] == "52.7.0":            
#Voltage level L2 in V (DSMR4)            
#1-0:52.7.0(00234*V) 
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_voltage_l2=int(float(p1_line[p1_num_start:p1_num_end]))
            p1_unit_voltage_l2=p1_line[p1_num_end+1:p1_lastpos]    

        elif p1_line[4:10] == "72.7.0":            
#Voltage level L3 in V (DSMR4)            
#1-0:72.7.0(00234*V) 
            p1_lastpos=len(p1_line)-1
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_voltage_l3=int(float(p1_line[p1_num_start:p1_num_end]))
            p1_unit_voltage_l3=p1_line[p1_num_end+1:p1_lastpos]  
            
        elif p1_line[4:11] == "96.13.1":
#Text message code: numeric 8 digits
#eg. 0-0:96.13.1()
            p1_lastpos=len(p1_line)-1
#        p1_message_code=p1_line[12:p1_lastpos]
            p1_message_code=bytes.fromhex(p1_line[12:p1_lastpos]).decode('utf-8')
        elif p1_line[4:11] == "96.13.0":
    #Text message max 1024 characters.
    #eg. 0-0:96.13.0()
            p1_lastpos=len(p1_line)-1
            p1_message_text=bytes.fromhex(p1_line[12:p1_lastpos]).decode('utf-8')
#        p1_line[12:p1_lastpos]
#####
#Channels 1/2/3/4: MBus connected meters
#####
        elif p1_line[4:10] == "24.1.0":
#Device-Type
#eg. 0-1:24.1.0(3)
#or 0-1:24.1.0(03) 3=Gas;5=Heat;6=Cooling
#or 0-1:24.1.0(03) 3/7=Gas;5=Heat;6=Cooling (Standard OBIS: 1-Electricity / 4-HeatCostAllocation / 5-Cooling / 6-Heat / 7-Gas / 8-ColdWater / 9-HotWater)

            p1_channel=int(p1_line[2:3])
            p1_lastpos=len(p1_line)-1
            p1_value=int(p1_line[11:p1_lastpos])
            if p1_value in [3,7]:
                 p1_value2="Gas"
            elif p1_value == 4:
                 p1_value2="HeatCost"                 
            elif p1_value == 5:
                 p1_value2="Heat"
            elif p1_value == 6:
                 p1_value2="Cold"
            elif p1_value == 8:
                 p1_value2="Cold water"
            elif p1_value == 9:
                 p1_value2="Hot water"
             
            else:
                 p1_value2="Unknown"
#self, id=None, type_id=None, type_desc=None, equipment_id=None, timestamp=None, meterreading=None, unit=None, valveposition=None
            if p1_channel==1:
                p1_channel_1.id=p1_channel
                p1_channel_1.type_id = p1_value
                p1_channel_1.type_desc= p1_value2
            elif p1_channel==2:
                p1_channel_2.id=p1_channel
                p1_channel_2.type_id = p1_value
                p1_channel_2.type_desc= p1_value2
            elif p1_channel==3:
                p1_channel_3.id=p1_channel
                p1_channel_3.type_id = p1_value
                p1_channel_3.type_desc= p1_value2
            elif p1_channel==4:
                p1_channel_4.id=p1_channel
                p1_channel_4.type_id = p1_value
                p1_channel_4.type_desc= p1_value2
                    

        elif p1_line[4:10] == "96.1.0":
#Equipment identifier
#eg. 0-1:96.1.0(3238303039303031303434303132303130)
            p1_channel=int(p1_line[2:3])
            p1_lastpos=len(p1_line)-1
            p1_value=p1_line[11:p1_lastpos]
#self, id=None, type_id=None, type_desc=None, equipment_id=None, timestamp=None, meterreading=None, unit=None, valveposition=None
            if p1_channel==1:
                p1_channel_1.equipment_id=p1_value
            elif p1_channel==2:
                p1_channel_2.equipment_id=p1_value
            elif p1_channel==3:
                p1_channel_3.equipment_id=p1_value
            elif p1_channel==4:
                p1_channel_4.equipment_id=p1_value

        elif p1_line[4:10] == "24.3.0":
#Last hourly value delivered to client (DSMR < V4)
#eg. Kamstrup/Iskraemeco:
#0-1:24.3.0(110403140000)(000008)(60)(1)(0-1:24.2.1)(m3)
#(00437.631)
#eg. Companion Standard:
#0-1:24.3.0(110403140000)(000008)(60)(1)(0-1:24.2.1)(m3)(00437.631)
            p1_channel=int(p1_line[2:3])
            p1_channel_timestamp="20"+p1_line[11:13]+"-"+p1_line[13:15]+"-"+p1_line[15:17]+" "+p1_line[17:19]+":"+p1_line[19:21]+":"+p1_line[21:23]
            p1_lastpos=len(p1_line)-1
#Value is in next line
            p1_unit=p1_line[p1_lastpos-2:p1_lastpos]
            p1_raw = ser.readline()
#        p1_str=str(p1_raw, "utf-8")
            p1_str=p1_raw
            if comport != 0:
                p1_str=str(p1_raw, "utf-8")
            p1_line=p1_str.strip()
#self, id=None, type_id=None, type_desc=None, equipment_id=None, timestamp= None, meterreading=None, unit=None, valveposition=None
            if p1_channel==1:
                p1_channel_1.timestamp=p1_channel_timestamp
                p1_channel_1.meterreading=float(p1_line[1:10])
                p1_channel_1.unit=p1_unit
            elif p1_channel==2:
                p1_channel_2.timestamp=p1_channel_timestamp
                p1_channel_2.meterreading=float(p1_line[1:10])
                p1_channel_2.unit=p1_unit
            elif p1_channel==3:
                p1_channel_3.timestamp=p1_channel_timestamp
                p1_channel_3.meterreading=float(p1_line[1:10])
                p1_channel_3.unit=p1_unit
            elif p1_channel==4:
                p1_channel_4.timestamp=p1_channel_timestamp
                p1_channel_4.meterreading=float(p1_line[1:10])
                p1_channel_4.unit=p1_unit

        elif p1_line[4:10] == "24.2.1":
#Last hourly value delivered to client (DSMR v4)
#eg. 0-1:24.2.1(101209110000W)(12785.123*m3)
            p1_channel=int(p1_line[2:3])
            p1_channel_timestamp="20"+p1_line[11:13]+"-"+p1_line[13:15]+"-"+p1_line[15:17]+" "+p1_line[17:19]+":"+p1_line[19:21]+":"+p1_line[21:23]
            p1_lastpos=len(p1_line)-1
            p1_line=p1_line[25:p1_lastpos]
            p1_lastpos=len(p1_line)
            p1_num_start = p1_line.find("(") +1
            p1_num_end = p1_line.find("*")
            p1_value=float(p1_line[p1_num_start:p1_num_end])        
            p1_unit=p1_line[p1_num_end+1:p1_lastpos]
#self, id=None, type_id=None, type_desc=None, equipment_id=None, timestamp= None, meterreading=None, unit=None, valveposition=None
            if p1_channel==1:
                p1_channel_1.timestamp=p1_channel_timestamp
                p1_channel_1.meterreading=p1_value
                p1_channel_1.unit=p1_unit
            elif p1_channel==2:
                p1_channel_2.timestamp=p1_channel_timestamp
                p1_channel_2.meterreading=p1_value
                p1_channel_2.unit=p1_unit
            elif p1_channel==3:
                p1_channel_3.timestamp=p1_channel_timestamp
                p1_channel_3.meterreading=p1_value
                p1_channel_3.unit=p1_unit
            elif p1_channel==4:
                p1_channel_4.timestamp=p1_channel_timestamp
                p1_channel_4.meterreading=p1_value
                p1_channel_4.unit=p1_unit

        elif p1_line[4:10] == "24.4.0":
#Valve position (on/off/released)
#eg. 0-1:24.4.0()
#eg. 0-1:24.4.0(1)
#Valveposition defaults to '1'(=Open) if invalid value
            p1_channel=int(p1_line[2:3])
            p1_lastpos=len(p1_line)-1
            p1_value=p1_line[12:p1_lastpos].strip()
            if not isinstance(p1_value, int):
               p1_value=1
            if p1_channel==1:
                p1_channel_1.valveposition=p1_value
            elif p1_channel==2:
                p1_channel_2.valveposition=p1_value
            elif p1_channel==3:
                p1_channel_3.valveposition=p1_value
            elif p1_channel==4:
                p1_channel_4.valveposition=p1_value

        elif p1_line[0:1] == "" or p1_line[0:1] == " ":
#Empty line
            p1_value=""
            
        elif p1_line[0:1] == "!":
#in DSMR 4 telegrams there might be a checksum following the "!".
#eg. !141B
#CRC16 value calculated over the preceding characters in the data message (from “/” to “!” using the polynomial: x16+x15+x2+1).
#the checksum is discarded
     
#End of P1 telegram
#Output if a complete telegram and matching log_interval
             if p1_teller == log_interval:
################################################################
#Start of functionality to add other meterdata to p1-telegram  #
################################################################
#Comment out / remove when not applicable                      #
################################################################
#                if import_db:
######################HEAT: Mandatory 1st ChannelID, 1st ChannelDataElement, optional 2nd ChannelID, 2nd ChannelDataElement
#                   get_heat_data(1,p1_channel_1,2,p1_channel_2)
######################POWER SUB METERING: ChannelID, ChannelDataElement, TypeID, TypeDescription
#                   get_power_data(#,p1_channel_#,1,"E-Production volume")
######################S0 SUB METERING: S0-ID, S0-Register, ChannelID, ChannelDataElement, TypeID, TypeDescription
#                   get_s0_data('25325','1',3,p1_channel_3,1,"E-Production volume")
######################PV INVERTER: Mandatory 1st ChannelID, 1st ChannelDataElement, optional 2nd ChannelID, 2nd ChannelDataElement
#                   get_pv_data(1,p1_channel_1,2,p1_channel_2)
################################################################
#End of functionality to add other meterdata to p1-telegram    #
################################################################
#Output to screen
                if output_mode=="screen": print_p1_telegram()
#Output to csv_file
                if output_mode=="csv": csv_p1_telegram()
#Output to json_file
                if output_mode=="json": json_p1_telegram()                
#Output to database
                if output_mode=="db": db_p1_telegram()
#Output to PVOutput.org
                if pvo_output: pvo_p1_telegram()
################################################################
                p1_teller=0
                p1_telegram=False
#to facilitate testing, when reading p1test.log always wait 10 seconds before proceeding to next telegram to simulate actual meter behaviour           
             if comport == 0: sleep(10)
        else:
#Always dump unrecognized data in identified telegram to screen
            print ("Error interpreting P1-telegram, unrecognized data encountered: '%s'" % p1_line )
#    elif p1_line != '':
#Always dump unrecognized data in identified telegram to screen    
#        print ("Fout bij analyseren P1 data, nog geen compleet P1-telegram ontvangen: '%s'" % p1_line )

#Close port and show status
try:
    ser.close()
except:
    if win_os:
        sys.exit ("Error closing %s. Program aborted."  % ser.name)
    else:
        sys.exit ("Error closing %s. Program aborted."  %  port)  
      









