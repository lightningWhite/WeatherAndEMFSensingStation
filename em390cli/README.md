# EMF-390 Command Line Client

Use command `emf390cli -h` to display available commands: 

```
EMF-390 CLI 0.1.0
Davide Dal Farra <dalfarra@codref.com>
Provides simple CLI interface to EMF-390

USAGE:
    emf390cli [FLAGS] [OPTIONS]

FLAGS:
    -c, --csv            Export fetched values as a CSV string.
    -B, --getbanddata    Retrieve the Spectrum Data from device
    -h, --help           Prints help information
    -j, --json           Export fetched values as a JSON string.
    -l, --list           List serial ports available on system
    -V, --version        Prints version information

OPTIONS:
    -a, --amount <amount>        Specify the amount of data to retrieve using address:amount.
                                                 For example 0:4000 retrieve the first 1000 bytes of data.Comman
                                                 Minum amount is 4000, maximum amount is 1000000
    -d, --download <download>    Download data stored on device into the specified file
    -f, --format <format>        Fetch values and returns a JSON object string
                                 Accepted values are:
                                         %w:  Retrieve RF Watt from device
                                         %d:  Retrieve RF -dBm from device
                                         %e:  Retrieve the Density from device
                                         %t:  Retrieve the Total Density from device
                                         %k:  Retrieve the Total Density Peak from device
                                         %E:  Retrieve the EF value from device
                                         %M:  Retrieve the EMF value from device
    -i, --influx <influx>        Export fetched values as InfluxDB string.
    -p, --port <port>            Specify the serial port to use
```

## Read data in real-time from the device

Data can be read, in real time, from the device using three different formats:  

* CSV: specify the ```-c``` flag
* JSON: specify the ```-j``` flag
* InfluxDB: specify the ```-i``` flag followed by a *measurement* name, i.e. ``` -i myroom

In order to read data, a format must be passed.  
The format allows to fetch only specific values (and consider that not all the values are available on all mode of the device).  
Suggested mode is **vertical**, and suggested format is ```%w%d%e%t%k%E%M``` which actually reatrieve all data available in vertical mode:  

```
$ emf390cli -p /dev/ttyUSB0 -f '%w%d%e%t%k%E%M' --influx 'statuto_'

statuto_rfwatts,raw_value_unit="pW",mhz_unit="MHz" value=0.000000000158,raw_value=158,mhz=624
statuto_rfdbm,raw_value_unit="dbm",mhz_unit="MHz" value=-68,raw_value=-68,mhz=624
statuto_rfdensity,raw_value_unit="mW/m2",mhz_unit="MHz" value=0.0001,raw_value=0.1,mhz=624
statuto_rftotaldensity,raw_value_unit="mW/m2",mhz_unit="n/a" value=0.0831,raw_value=83.1,mhz=0
statuto_rftotaldensitypeak,raw_value_unit="mW/m2",mhz_unit="n/a" value=0.6354,raw_value=635.4,mhz=0
statuto_ef,raw_value_unit="V/m",mhz_unit="n/a" value=16.6,raw_value=16.6,mhz=0
statuto_emf,raw_value_unit="mG",mhz_unit="n/a" value=2.0,raw_value=2.0,mhz=0
```

or in CSV format:  

```
$ emf390cli -p /dev/ttyUSB0 -f '%w%d%e%t%k%E%M' --csv

rfwatts, 0.000000000158, 158, pW, 672, MHz
rfdbm, -68, -68, dbm, 672, MHz
rfdensity, 0.0001, 0.1, mW/m2, 672, MHz
rftotaldensity, 0.06720000000000001, 67.2, mW/m2, 0, n/a
rftotaldensitypeak, 0.6354, 635.4, mW/m2, 0, n/a
ef, 11.8, 11.8, V/m, 0, n/a
emf, 0.6, 0.6, mG, 0, n/a
```

or in JSON format:  
```
$ emf390cli -p /dev/ttyUSB0 -f '%w%d%e%t%k%E%M' --json

[{"name":"rfwatts","values":{"value":"0.0000000002","raw_value":"200","raw_value_unit":"pW","mhz":"624","mhz_unit":"MHz"}},{"name":"rfdbm","values":{"value":"-67","raw_value":"-67","raw_value_unit":"dbm","mhz":"624","mhz_unit":"MHz"}},{"name":"rfdensity","values":{"value":"0.0001","raw_value":"0.1","raw_value_unit":"mW/m2","mhz":"624","mhz_unit":"MHz"}},{"name":"rftotaldensity","values":{"value":"0.0045","raw_value":"4.5","raw_value_unit":"mW/m2","mhz":"0","mhz_unit":"n/a"}},{"name":"rftotaldensitypeak","values":{"value":"0.6354","raw_value":"635.4","raw_value_unit":"mW/m2","mhz":"0","mhz_unit":"n/a"}},{"name":"ef","values":{"value":"7.1","raw_value":"7.1","raw_value_unit":"V/m","mhz":"0","mhz_unit":"n/a"}},{"name":"emf","values":{"value":"0.9","raw_value":"0.9","raw_value_unit":"mG","mhz":"0","mhz_unit":"n/a"}}]
```

To retrieve just one value, specify a different format string. For example to obtain just the RF dbm:  

```
$ emf390cli -p /dev/ttyUSB0 -f '%d' --json

[{"name":"rfdbm","values":{"value":"-68","raw_value":"-68","raw_value_unit":"dbm","mhz":"672","mhz_unit":"MHz"}}]
```

## Retrieve data stored inside the unit memory

The tool can be used to fetch values stored inside device memory (up to 1MB).  
In this case all the values are exported at once (EF, EMF and RF data converted in various units).  
The default file format is CSV (comma separated values), but InfluxDB can be choose to export as a file suitable to InfluDB API.  

To retrive the first 10K bytes from the ROM as CSV format:  

```
$ emf390cli -p /dev/ttyUSB0 -d out.csv -a 0:10000
```

A file named out.csv will be saved locally to the command.  
To retrieve **all** rom data, just remove the ```-a``` option.  
The system scans for a set of continuous FF bytes (more precisely 20). In case it considers the data as "completed" and does not continue with the fetching (which can last for minutes).  

To retrieve all the data and store it as InfluxDB format:  

```
$ emf390cli -p /dev/ttyUSB0 -d out.csv -i myroom
```

The software is still a bit raw and does not provide much information while processing the data. It might seem stuck but it's actually working.  
Just be patient - as it might require some minute to complete.  

## Linux

```
cargo build
```

## Windows

The software has been tested and compiled in Linux, but a Windows version is available and can be easily compiled (if you have Rust installed).  
In windows the serial ports listing does not seem to work. Other commands works well.  
In order to "find" the correct port, you can either use the official software or you can try several ```COM```, like ```COM1```, ```COM2```, etc.  
My windows system uses COM3.  

```
cargo build --target=x86_64-pc-windows-gnu
```

## Arm (Raspberry Pi)

Real time data retrieval works and has been deeply tested. Never tried to download data from Arm.  
I used some bit operations which does not consider the endianess of the integers. It might not work without some godd refactoring.

```
export CARGO_TARGET_ARM_UNKNOWN_LINUX_MUSLEABIHF_LINKER=arm-linux-gnueabihf-gcc
export CC_arm_unknown_linux_musleabihf=arm-linux-gnueabihf-gcc
cargo build --target=arm-unknown-linux-musleabihf
```

## Mac OSX Darwin

I do not own a Mac but might be useful for someone.  
Below a note about how to add cross-compile support on linux to x86/64 OSX Darwin.

```
rustup target add x86_64-apple-darwin
```
Configure linker on ```~/.cargo/config``` file
```
[target.x86_64-apple-darwin]
linker = "x86_64-apple-darwin15-clang"
ar = "x86_64-apple-darwin15-ar"
```
Install OSXCross
```
git clone https://github.com/tpoechtrager/osxcross
cd osxcross
wget https://s3.dockerproject.org/darwin/v2/MacOSX10.11.sdk.tar.xz
mv MacOSX10.11.sdk.tar.xz tarballs/
sed -i -e 's|-march=native||g' build_clang.sh wrapper/build.sh
UNATTENDED=yes OSX_VERSION_MIN=10.7 ./build.sh
sudo mkdir -p /usr/local/osx-ndk-x86
sudo mv target/* /usr/local/osx-ndk-x86
```
Compile the emf390cli with debug symbols:
```
export PATH=/usr/local/osx-ndk-x86/bin:$PATH
export PKG_CONFIG_ALLOW_CROSS=1
cargo build --target=x86_64-apple-darwin
```

## Binary distribution  

The software is meant to be distributed "as source". If you want to try it out, the build directory contains some executable, but it's at your own risk.  
They are build with Debug info.  

## Notes

To use the device for real-time data logging, remove the battery. The charging circuit is not shielded and you are going to collect a lot of interference with the battery on.  

