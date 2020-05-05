extern crate clap;
extern crate regex;
extern crate serde;
extern crate serde_json;
extern crate serialport;
extern crate chrono;

#[macro_use]
extern crate serde_derive;

use std::fs::File;
use std::io::{self, Write};
use std::string::FromUtf8Error;
use std::time::Duration;

use clap::{App, Arg};
use regex::Regex;
use serialport::prelude::*;
use chrono::{NaiveDate, NaiveDateTime};

#[derive(Serialize, Deserialize)]
struct Command {
    name: String,
    values: Value,
}
#[derive(Serialize, Deserialize)]
struct Value {
    value: String,
    raw_value: String,
    raw_value_unit: String,
    mhz: String,
    mhz_unit: String,
}

#[repr(C)]
union DataFloatUnion {
    f: f32,
    c: [u8; 4],
}

struct DataStruct {
    emf: f32,
    ef: f32,
    rf_pw_sqcm: f32,
    rf_mw_sqcm: f32,
    rf_mw_sqm: f32,
}

fn get_values(raw_string: &str, is_total: bool) -> Value {
    let re: Regex;
    let mut raw_value = "0";
    let mut raw_value_unit = "n/a";
    let mut mhz = "0";
    let mut mhz_unit = "n/a";
    if !is_total {
        re = Regex::new(r"([0-9\.\-]+)\s([a-zA-z0-9/]+)\(\-?([0-9\.]+)\s([a-zA-Z]+)\)").unwrap();
    } else {
        re = Regex::new(r"([0-9\.\-]+)\s([a-zA-z0-9/]+).*").unwrap();
    }

    if raw_string.len() > 0 {
        match re.captures(raw_string) {
            Some(v) => {
                raw_value = v.get(1).map_or("", |m| m.as_str());
                raw_value_unit = v.get(2).map_or("", |m| m.as_str());
                if !is_total {
                    mhz = v.get(3).map_or("", |m| m.as_str());
                    mhz_unit = v.get(4).map_or("", |m| m.as_str());
                }
            }
            None => {}
        }
    }
    Value {
        value: convert_value(&raw_value, &raw_value_unit),
        raw_value: raw_value.to_string(),
        raw_value_unit: raw_value_unit.to_string(),
        mhz: mhz.to_string(),
        mhz_unit: mhz_unit.to_string(),
    }
}

fn convert_value(value: &str, unit: &str) -> String {
    match unit {
        "pW" => value
            .parse::<f64>()
            .map(|n| n / 1000000000000.0)
            .unwrap()
            .to_string(),
        "nW" => value
            .parse::<f64>()
            .map(|n| n / 1000000000.0)
            .unwrap()
            .to_string(),
        "uW" => value
            .parse::<f64>()
            .map(|n| n / 1000000.0)
            .unwrap()
            .to_string(),
        "mW" => value
            .parse::<f64>()
            .map(|n| n / 1000.0)
            .unwrap()
            .to_string(),
        "mW/m2" => value
            .parse::<f64>()
            .map(|n| n / 1000.0)
            .unwrap()
            .to_string(),
        _ => return value.to_string(),
    }
}

fn list_serial_ports() {
    if let Ok(ports) = serialport::available_ports() {
        match ports.len() {
            0 => println!("No ports found."),
            1 => println!("Found 1 port:"),
            n => println!("Found {} ports:", n),
        };
        for p in ports {
            println!("  {}", p.port_name);
        }
    } else {
        print!("Error listing serial ports");
    }
}

fn r(port: &mut Box<SerialPort>, termination_char: u8) -> Result<String, FromUtf8Error> {
    String::from_utf8(r_hex(port, true, termination_char))
}

fn r_hex(port: &mut Box<SerialPort>, has_termination: bool, termination_char: u8) -> Vec<u8> {
    let mut serial_buf: Vec<u8>;
    if termination_char.is_ascii() {
        serial_buf = vec![0; 1];
    } else {
        serial_buf = vec![0; 32];
    }
    let mut out: Vec<u8> = Vec::new();
    loop {
        match port.read(serial_buf.as_mut_slice()) {
            Ok(t) => {
                out.extend_from_slice(&mut serial_buf[..t]);
                if has_termination
                    && termination_char.is_ascii()
                    && serial_buf[0] == termination_char
                {
                    break;
                }
            }
            Err(ref e) if e.kind() == io::ErrorKind::TimedOut => (break),
            Err(e) => eprintln!("{:x?}", e),
        }
    }
    out
}

fn w(command: &str, port: &mut Box<SerialPort>) {
    if port.write(command.as_bytes()).unwrap() == 0 {
        eprintln!("Failed to write \"{}\" command to device.", command);
        ::std::process::exit(1);
    }
}

fn w_hex(command: &[u8], port: &mut Box<SerialPort>) {
    if port.write(command).unwrap() == 0 {
        eprintln!("Failed to write command to device.");
        ::std::process::exit(1);
    }
}

fn exec_command(
    command: &str,
    command_name: &str,
    port: &mut Box<SerialPort>,
    is_total: bool,
    termination_char: char,
) -> Command {
    w(command, port);
    let o = r(port, termination_char as u8).unwrap();
    Command {
        name: command_name.to_string(),
        values: get_values(o.as_str(), is_total),
    }
}

fn to_csv(commands: &Vec<Command>) -> String {
    let mut csv = "".to_string();
    for c in commands {
        csv = format!(
            "{}{}",
            csv,
            format!(
                "{name}, {value}, {raw_value}, {raw_value_unit}, {mhz}, {mhz_unit} \n",
                name = c.name,
                value = c.values.value,
                raw_value = c.values.raw_value,
                raw_value_unit = c.values.raw_value_unit,
                mhz = c.values.mhz,
                mhz_unit = c.values.mhz_unit
            )
        );
    }
    csv
}

fn to_influx(commands: &Vec<Command>, prefix: &str) -> String {
    let mut csv = "".to_string();
    for c in commands {
        csv = format!("{}{}", csv, format!(
            "{prefix}{name},raw_value_unit=\"{raw_value_unit}\",mhz_unit=\"{mhz_unit}\" value={value},raw_value={raw_value},mhz={mhz}\n",
            prefix=prefix, name=c.name, value=c.values.value, raw_value=c.values.raw_value,
            raw_value_unit=c.values.raw_value_unit, mhz=c.values.mhz, mhz_unit=c.values.mhz_unit
        ));
    }
    csv
}

fn download_data(port: &mut Box<SerialPort>, output_file_name: &str, addr: u32, max_amount: u32, influx_prefix: &str) -> std::io::Result<()> {
    let amount: u16 = 4000;
    let mut address: u32 = addr;
    let mut o = vec![0u8];
    let mut output_file = File::create(output_file_name)?;

    while address < max_amount {
        let command = &[
            0x3cu8,0x53u8,0x50u8,0x49u8,0x52u8, // <SPIR
            (address >> 16) as u8,(address >> 8) as u8,address as u8, // ADDRESS
            (amount >> 8) as u8,amount as u8, // AMOUNT
            0x3eu8,0x3eu8, // >>
        ];

        println!(
            "[{:.2}%]\tRetrieving {} bytes out of {}. Current size is {} bytes",
            ((address as f32 / max_amount as f32) * 100.0),
            address,
            max_amount,
            o.len()
        );

        w_hex(command, port);
        o.append(&mut r_hex(port, false, 0));

        if is_ff(&o[o.len()-20..o.len()]) {
            println!("\tNo more data on device");

            break;
        }
        address += amount as u32;
    }
    println!("[100%]\tRetrieved all data");

    let mut i = 0;
    let mut timestamp = NaiveDate::from_ymd(1981, 8, 15).and_hms(23, 45, 00).timestamp();
    while i < o.len() - 1 {
        if o[i] == 0x55u8 && o[i + 1] == 0xAAu8 {
            timestamp = parse_date(&o[i + 2..i + 8]).timestamp();
            i += 8;
        } else if o[i] == 0xAAu8 && o[i + 1] == 0x55u8 {
            let d = parse_data(&o[i + 2..i + 12]);
            if influx_prefix != "" {
                write!(output_file,
                    "{influx_prefix}emf value={emf} {timestamp}\n{influx_prefix}ef value={ef} {timestamp}\n{influx_prefix}rf value={rf_mw_sqm},value2={rf_mw_sqcm},value3={rf_pw_sqcm} {timestamp}\n",
                    influx_prefix=influx_prefix, emf=d.emf, ef=d.ef, rf_mw_sqm=d.rf_mw_sqm, rf_mw_sqcm=d.rf_mw_sqcm, rf_pw_sqcm=d.rf_pw_sqcm, timestamp=timestamp
                )?;
            } else {
                write!(output_file,
                    "{},{},{},{},{},{},{}\n",
                    timestamp, NaiveDateTime::from_timestamp(timestamp, 0), d.emf, d.ef, d.rf_mw_sqm, d.rf_mw_sqcm, d.rf_pw_sqcm
                )?;
            }
            timestamp += 1;
            i += 12;
        } else {
            i += 1;
        }
    }
    Ok(())
}

fn is_ff(data: &[u8]) -> bool {
    for x in data {
        if *x != 0xFFu8 {
            return false
        }
    }
    println!("\tLast 20 bytes were: {:X?}", data);
    true
}

fn parse_date(data: &[u8]) -> NaiveDateTime {
    NaiveDate::from_ymd( 2000 + (data[0] as i32), data[1] as u32,  data[2] as u32).and_hms( data[3] as u32,  data[4] as u32,  data[5] as u32)
}

fn parse_data(data: &[u8]) -> DataStruct {
    let emf = ((data[0] as u16) << 8) | data[1] as u16;
    let emf_dec = (emf & 0b1111) as u16;
    let emf_uni = (emf & 0b1111111111110000) as u16;

    let ef;
    let rf;
    let mut u = DataFloatUnion { f: 0.0 };
    unsafe {
        u.c = [data[2], data[3], data[4], data[5]];
        ef = u.f;
    }
    unsafe {
        u.c = [data[6], data[7], data[8], data[9]];
        rf = u.f
    }

    DataStruct {
        emf: format!("{}.{}", emf_uni, emf_dec).parse().unwrap(),
        ef: ef,
        rf_pw_sqcm: rf,
        rf_mw_sqcm: rf / 1000000000.0,
        rf_mw_sqm: rf / 100000.0,
    }
}

fn main() {
    let matches = App::new("EMF-390 CLI")
        .version("0.1.0")
        .author("Davide Dal Farra <dalfarra@codref.com>")
        .about("Provides simple CLI interface to EMF-390")
        .arg(
            Arg::with_name("listSerialPorts")
                .short("l")
                .long("list")
                .help("List serial ports available on system"),
        )
        .arg(
            Arg::with_name("port")
                .short("p")
                .long("port")
                .help("Specify the serial port to use")
                .takes_value(true),
        )
        // Vertical mode commands
        .arg(
            Arg::with_name("format")
                .short("f")
                .long("format")
                .help(
                    "Fetch values and returns a JSON object string
Accepted values are:
        %w:  Retrieve RF Watt from device
        %d:  Retrieve RF -dBm from device
        %e:  Retrieve the Density from device
        %t:  Retrieve the Total Density from device
        %k:  Retrieve the Total Density Peak from device
        %E:  Retrieve the EF value from device
        %M:  Retrieve the EMF value from device\n",
                )
                .takes_value(true),
        )
        .arg(
            Arg::with_name("csv")
                .short("c")
                .long("csv")
                .help("Export fetched values as a CSV string."),
        )
        .arg(
            Arg::with_name("json")
                .short("j")
                .long("json")
                .help("Export fetched values as a JSON string."),
        )
        .arg(
            Arg::with_name("influx")
                .short("i")
                .long("influx")
                .help("Export fetched values as InfluxDB string.")
                .takes_value(true),
        )
        // Spectrum mode
        .arg(
            Arg::with_name("getbanddata")
                .short("B")
                .long("getbanddata")
                .help("Retrieve the Spectrum Data from device"),
        )
        // retrieve stored data
        .arg(
            Arg::with_name("download")
                .short("d")
                .long("download")
                .help("Download data stored on device into the specified file")
                .takes_value(true),
        )
        .arg(
            Arg::with_name("amount")
                .short("a")
                .long("amount")
                .help("Specify the amount of data to retrieve using address:amount.
                For example 0:4000 retrieve the first 1000 bytes of data.Comman
                Minum amount is 4000, maximum amount is 1000000")
                .takes_value(true),
        )        
        .get_matches();

    if matches.is_present("list") {
        list_serial_ports()
    } else if matches.is_present("port") {
        let port_name = matches.value_of("port").unwrap();
        let mut settings: SerialPortSettings = Default::default();
        settings.data_bits = DataBits::Eight;
        settings.flow_control = FlowControl::None;
        settings.parity = Parity::None;
        settings.stop_bits = StopBits::One;
        settings.timeout = Duration::from_millis(400);
        settings.baud_rate = 115200;

        match serialport::open_with_settings(&port_name, &settings) {
            Ok(mut port) => {
                if matches.is_present("format") {
                    let items = matches.value_of("format").unwrap().split("%");
                    let mut commands: Vec<Command> = Vec::new();
                    for s in items {
                        if s == "w" {
                            commands.push(exec_command(
                                "<GETRFWATTS>>",
                                "rfwatts",
                                &mut port,
                                false,
                                ')',
                            ));
                        }
                        if s == "d" {
                            commands.push(exec_command(
                                "<GETRFDBM>>",
                                "rfdbm",
                                &mut port,
                                false,
                                ')',
                            ));
                        }
                        if s == "e" {
                            commands.push(exec_command(
                                "<GETRFDENSITY>>",
                                "rfdensity",
                                &mut port,
                                false,
                                ')',
                            ));
                        }
                        if s == "t" {
                            commands.push(exec_command(
                                "<GETRFTOTALDENSITY>>",
                                "rftotaldensity",
                                &mut port,
                                true,
                                ')',
                            ));
                        }
                        if s == "k" {
                            commands.push(exec_command(
                                "<GETRFTOTALDENSITYPEAK>>",
                                "rftotaldensitypeak",
                                &mut port,
                                true,
                                ')',
                            ));
                        }
                        if s == "E" {
                            commands.push(exec_command("<GETEF>>", "ef", &mut port, true, 'm'));
                        }
                        if s == "M" {
                            commands.push(exec_command("<GETEMF>>", "emf", &mut port, true, 'G'));
                        }
                    }

                    if matches.is_present("json") {
                        print!("{}", serde_json::to_string(&commands).unwrap());
                    } else if matches.is_present("influx") {
                        print!(
                            "{}",
                            to_influx(&commands, matches.value_of("influx").unwrap())
                        );
                    } else {
                        print!("{}", to_csv(&commands));
                    }
                } else if matches.is_present("getbanddata") {
                    w("<GETBANDDATA>>", &mut port);
                    let o = r(&mut port, 0).unwrap();
                    print!("{}", o.as_str());
                } else if matches.is_present("download") {
                    let output_file_name = matches.value_of("download").unwrap();
                    let mut amount = "0:994000";
                    if matches.is_present("amount") {
                        amount = matches.value_of("amount").unwrap();
                    }
                    let params: Vec<&str> = amount.split(":").collect();
                    if params.len() < 2 {
                        eprintln!("Failed to parse \"{}\". Accepted format is address:amount", amount);
                        ::std::process::exit(1);
                    }
                    let address: u32 = params[0].parse().unwrap();
                    let max_amount: u32 = params[1].parse().unwrap();
                    if max_amount < 4000 || max_amount > 994000 || address > 994000 {
                        eprintln!("Range not valid");
                        ::std::process::exit(1);
                    }

                    let mut influx = "";
                    if matches.is_present("influx") {                    
                        influx = matches.value_of("influx").unwrap();
                    } 
                    download_data(&mut port, output_file_name, address, max_amount, influx); 
                }
            }
            Err(e) => {
                eprintln!("Failed to open \"{}\". Error: {}", port_name, e);
                ::std::process::exit(1);
            }
        }
    }
}
