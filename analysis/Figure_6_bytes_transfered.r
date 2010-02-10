
# ============================================================================
# PLOT 3
# Create a line graph of measured data transfer in bytes
# ----------------------------------------------------------------------------
# Parameters
#
# file,highest_rate,attempted_rate,avg_data
# test_freq_12_per_day_traditional.txt,133.600000,135,159456.000000
# test_freq_2_per_day_tokyo.txt,226.200000,193,61086.000000
# test_freq_24_per_day_synckit.txt,580.500000,503,13365.000000
#
# ============================================================================

tp <- read.csv("apache.csv",
    header=T,
    dec='.',
    na.strings=c('XXXXXXX')
)

# Aggregate across all the merged CSV file (this file should contain all 3)

# Average the data across each strategy
tpAgg <- aggregate(tp, 
                   by=list(tp$file, tp$strategy, tp$frequency), 
                   FUN=mean, 
                   na.rm=TRUE)

plot_colors <- c(rgb(r=0.0,g=0.0,b=0.9), "red", "forestgreen")

# Start PDF device driver to save output to figure.pdf
pdf(file="avg_data.pdf", height=3.5, width=5)

# Trim off excess margin space (bottom, left, top, right)par(mar=c(4.2, 3.8, 0.2, 0.2))
par(mar=c(4.2, 3.8, 0.2, 0.2))


# Graph autos using a y axis that uses the full range of value
# in autos_data. Label axes with smaller font and use larger 
# line widths.
plot(
    x=tpAgg[tpAgg$Group.2 == "Traditional",]$frequency*12/12.631578947,
    y=tpAgg[tpAgg$Group.2 == "Traditional",]$avg_data, 
    type="o", 
       col=plot_colors[1], 
       ylim=range(tpAgg$avg_data), 
       ann=T, 
       xlab="Visit Frequency (relative to update)",
       ylab="Data Transferred (Bytes/Request)", 
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
    tpAgg[tpAgg$Group.2 == "Flying Templates",]$frequency*12/12.631578947,
    tpAgg[tpAgg$Group.2 == "Flying Templates",]$avg_data,
    type="o", 
    lty=1, 
    lwd=2, 
    col=plot_colors[2]
)
# 
# # Graph SK with thicker green dotted line
lines(
    tpAgg[tpAgg$Group.2 == "Sync Kit",]$frequency*12/12.631578947,
    tpAgg[tpAgg$Group.2 == "Sync Kit",]$avg_data,
    type="o", 
    lty=1, 
    lwd=2, 
    col=plot_colors[3]
)

# Create a legend in the top-left corner that is slightly  
# smaller and has no border
legend(2.8, 170000, c("Traditional", "Flying Templates", "Sync Kit"), cex=0.6, col=plot_colors, lty=1, lwd=2, bty="n");
  
# Turn off device driver (to flush output to PDF)
dev.off()


# Restore default margins
par(mar=c(5, 4, 4, 2) + 0.1)

