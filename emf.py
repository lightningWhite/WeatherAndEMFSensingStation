# EMF-390 Sensor
#
# Uses the EMF-390 sensor to read 
#
#




# Radio Frequency (Watts)
 - 





rfwatts, 0.000000000158, 158, pW, 672, MHz
rfdbm, -68, -68, dbm, 672, MHz
rfdensity, 0.0001, 0.1, mW/m2, 672, MHz
rftotaldensity, 0.06720000000000001, 67.2, mW/m2, 0, n/a
rftotaldensitypeak, 0.6354, 635.4, mW/m2, 0, n/a
ef, 11.8, 11.8, V/m, 0, n/a
emf, 0.6, 0.6, mG, 0, n/a



RF Watts (W), RF Watts Frequency (MHz), RF dBm (dBm), RF dBm Frequency (MHz), RF Density (W/m2), RF Density Frequency (MHz), RF Total Density (W/m2), RF Total Density 15 min Peak (W/m2), EF (V/m), EMF (mG)


A few notes:

rfwatts and rfdbm are different forms of the same number. The problem is that it appears
that they are calculated sequentially. This means that the readings of the sensor may be
different for each reading. This is no bueno. They should not contradict each other. I
will probably want to take one or the other and then convert it to the other form if it's
desirable to have both. Or I could just use one or the other. I may need to look into the
rfdensity, because it's likely directly tied to the reading.

When I start preprocessing the data, I will probably want to look into binning the data.
Since the frequency is directly related to the power (magnitude of the wave), I probably
don't want those to be treated as independent values when machine learning with them.
What I may end up doing is grouping the power readings into categories of common frequencies
like 0-400MHz, 401-999MHz, 1000-3000MHz, etc. and then put the power values in each category.
I can do that later though if I gather the data.