import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataFunctions import decayThreshold, linearFit, fit_bootstrap, fit_bootstrap_full
import matplotlib.pyplot as plt

# load the excel sheet
excel_file = pd.ExcelFile("Cleaned_PhotoelectricData.xlsx")

# initalize the array of stopping voltages and arrays for later planks constant calculation
V_stopping = []
V_stopping_variation = []
h_x = []
h_y = []


#Create a function "recipe" for the bootstrap algorithm to use
line_recipe = lambda x, p: p[0] * x + p[1]



# Physical constants
c = 2.99792458e8     # m/s
e = 1.602176634e-19  # C

# index of wavelength in nanometers
wavelengths = [254.0e-9, 590.0e-9, 546.0e-9, 405.0e-9, 590.0e-9] # given by the manual 

# Iterate directly through sheet names using an if-statement
for sheet in excel_file.sheet_names:
    if sheet.startswith("VvC"):
        df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=1)
        df.columns = df.columns.str.strip()

        # Extract V and I arrays
        V = df["Voltage (V)"].values
        I = df["Photocurrent (uA)"].values #uA is microamperes 

        V = np.array([round(float(item), 1) for item in V]) # our measurements were consistent only to the tenths place
        I = np.array([round(float(item), 1) for item in I]) # this ensures that floating point error is minimized

        fastDecayRegion, slowDecayRegion = decayThreshold(I, V)

        #V and I values in the fast decay and the slow decay region 
        V_fastDecay = V[fastDecayRegion]
        I_fastDecay = I[fastDecayRegion] 

        V_slowDecay = V[slowDecayRegion]
        I_slowDecay = I[slowDecayRegion]

        slope_fast, intercept_fast = linearFit(V_fastDecay, I_fastDecay) # f1
        slope_slow, intercept_slow = linearFit(V_slowDecay, I_slowDecay) # f2

        # we can now estimate the stopping voltage by averaging our data
        # V = -intercept/slope when I = 0 
        V_1 = -intercept_fast / slope_fast

        # now we need a second point that starts from the same point, but intersects with the high v region
        V_2 = V_1 + (intercept_slow - intercept_fast) / (slope_fast - slope_slow) #V_1 - ((slope_slow * V_1) + intercept_slow) / (slope_slow) # Newton-Raphson where F = f1 - f2  and slope in high v region is very small

        
        V_stoppingAverage = (V_1 + V_2) / 2

        V_stopping.append(float(V_stoppingAverage)) # ensures that the output data type is float and not np.float64

        # the error must be propagated from here 
        # each of these saves two coloums each consisting of 100000 rows
        # coloumn zero contains slopes, one contains intercepts
        boot_fast = fit_bootstrap([slope_fast, intercept_fast], V_fastDecay, I_fastDecay, line_recipe, yerr_systematic=0.50)
        boot_slow = fit_bootstrap([slope_slow, intercept_slow], V_slowDecay, I_slowDecay, line_recipe, yerr_systematic=0.50)
        
       
        boot_slopes_fast = boot_fast[:, 0]
        boot_intercepts_fast = boot_fast[:, 1]

        boot_slopes_slow = boot_slow[:, 0]
        boot_intercepts_slow = boot_slow[:, 1]

        #voltage math again
        V_1_boot = - boot_intercepts_fast / boot_slopes_fast
        V_2_boot = V_1_boot + (boot_intercepts_slow - boot_intercepts_fast) / (boot_slopes_fast - boot_slopes_slow)
        V_avg_boot = (V_1_boot + V_2_boot) / 2 # will return 100000 V averages which allows us to find the deviation 

        # Multiplied by 2 for a 95.44% confidence interval
        V_stopping_variation.append(2 * np.std(V_avg_boot))

        # I also want to graph the line fits for later analysis
        plt.figure()

        # plot the data, and two lines
        plt.scatter(V, I, color='blue', label='Smoothed Data') 
        plt.plot(V, slope_fast*V + intercept_fast, "r--", linewidth = 1.5, label=f"Line 1 ($I_f$, $V_1$ = {V_1:.3f} V)")
        plt.plot(V, (-intercept_fast/V_2)*V + intercept_fast, "b--", linewidth=1.5, label=f"Line 2 ($I_s$, $V_2$ = {V_2:.3f} V)")

        # Mark the calculated stopping voltage average
        plt.axvline(x=V_stoppingAverage, color='red', linestyle=':', label=f'V_avg = {V_stoppingAverage:.2f} V')

        # Formatting
        plt.xlabel('Voltage (V)')
        plt.ylabel('Photocurrent (\u03bcA)')
        plt.title('Photocurrent vs. Voltage: Linear Extrapolation Fit')
        plt.grid(True)
        plt.legend()
        plt.show()

        

       
wavelengths = np.array(wavelengths)
V_stopping = np.array(V_stopping)
V_stopping_variation = np.array(V_stopping_variation)


h_x = 1 / wavelengths
h_y = V_stopping  #Filter data was not called here as there are too few data points

h_slope, h_intercept = linearFit(h_x, h_y)

h = (h_slope * e) / c       #calculate planks constant
workFunction = abs(h_intercept) #calculate work function, absolute value because enerygy of the work function is always positive 

# deviation of h can be calculated with our uncertaitny 
h_params_mean, h_params_err = fit_bootstrap_full([h_slope, h_intercept], h_x, h_y, line_recipe, yerr_systematic=V_stopping_variation)

h_err = (h_params_err[0] * e) / c  
workFunction_err = h_params_err[1]

print(f"Stopping voltages: {np.round(V_stopping, 3)} +/- {np.round(V_stopping_variation, 3)}")
print(f"h: {h:e} +/- {h_err:e}")
print(f"Work Function: {workFunction:.3f} +/- {workFunction_err:.3f}")

# --- Graphing h with uncertainties ---
plt.figure(figsize=(8, 6))

# Plot data points with the bootstrap variation as error bars
plt.errorbar(h_x, h_y, yerr=V_stopping_variation, fmt='ko', capsize=4, label="V_stopping ± Variation")

# Plot the linear fit
fit_line = h_slope * h_x + h_intercept
plt.plot(h_x, fit_line, 'r--', label=f"Linear Fit\nSlope: {h_slope:.3e}")

plt.xlabel("Inverse Wavelength 1/λ (1/nm)")
plt.ylabel("Stopping Potential (V)")
plt.title("Determination of Planck's Constant")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)

plt.show()