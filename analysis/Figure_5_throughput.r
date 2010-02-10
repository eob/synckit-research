
# ============================================================================
# PLOT 3
# Create a line graph of measured server throughput
# ----------------------------------------------------------------------------
# Parameters

updateFrequency <- 4 # Updates per day

#
# file,highest_rate,attempted_rate,avg_data
# test_freq_12_per_day_traditional.txt,133.600000,135,159456.000000
# test_freq_2_per_day_tokyo.txt,226.200000,193,61086.000000
# test_freq_24_per_day_synckit.txt,580.500000,503,13365.000000
#
# ============================================================================

tp <- read.csv("apache.csv.example",
    header=T,
    dec='.',
    na.strings=c('XXXXXXX')
)

# Aggregate across all the merged CSV file (this file should contain all 3)

# Average the data across each strategy
tpAgg <- aggregate(tp, 
                   by=list(tp$file, tp$strategy), 
                   FUN=mean, 
                   na.rm=TRUE)

print(tpAgg)

plot_colors <- c(rgb(r=0.0,g=0.0,b=0.9), "red", "forestgreen")

# Start PDF device driver to save output to figure.pdf
# pdf(file="throughput.pdf", height=3.5, width=5)

# Trim off excess margin space (bottom, left, top, right)par(mar=c(4.2, 3.8, 0.2, 0.2))
par(mar=c(4.2, 3.8, 0.2, 0.2))  

# Graph autos using a y axis that uses the full range of value
# in autos_data. Label axes with smaller font and use larger 
# line widths.
plot(
    x=tpAgg[tpAgg$Group.2 == "Traditional",]$freq / updateFrequency, 
    y=tpAgg[tpAgg$Group.2 == "Traditional",]$highest_rate, 
    type="o",  # Type p is point, l is line, o is point+line
       col=plot_colors[1], 
       ylim=range(tpAgg$highest_rate), 
       ann=T, 
       xlab="Visit Frequency (relative to update)",
       ylab="Server Throughput (Pages/s)", 
       cex.lab=0.8, 
       lwd=2
)

# # Make x axis tick marks without labels
# axis(1, lab=F)
# 
# # Plot y axis with smaller horizontal labels 
# axis(1, at=points[seq(7, length(points), 7)], lab=points[seq(7, length(points), 7)])
# axis(2, las=1, cex.axis=0.8)

# Create box around plot
box()

# 
# # Graph FT with thicker red dashed line
lines(
    tpAgg[tpAgg$Group.2 == "Flying Templates",]$freq / updateFrequency,
    tpAgg[tpAgg$Group.2 == "Flying Templates",]$highest_rate,
    type="o", 
    lty=1, 
    lwd=2, 
    col=plot_colors[2]
)

# 
# # Graph SK with thicker green dotted line
lines(
    tpAgg[tpAgg$Group.2 == "Sync Kit",]$freq / updateFrequency,
    tpAgg[tpAgg$Group.2 == "Sync Kit",]$highest_rate,
    type="o", 
    lty=1, 
    lwd=2, 
    col=plot_colors[3]
)

# Create a legend in the top-left corner that is slightly  
# smaller and has no border
legend("topleft", c("Traditional", "Flying Templates", "Sync Kit"), cex=0.8, col=plot_colors, 
   lty=1, lwd=2, bty="n");
  
# Turn off device driver (to flush output to PDF)
# dev.off()

# Restore default margins
par(mar=c(5, 4, 4, 2) + 0.1)

