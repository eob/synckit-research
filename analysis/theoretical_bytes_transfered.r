# ============================================================================
# PLOT 2
# Theoretical Bytes Transferred
# ----------------------------------------------------------------------------
# Parameters
#
templateSize <- 400
dataItemSize <- 50
dataTemplateSize <- 100
itemsPerPage <- 10
scaleMin <- 0.1
scaleMax <- 10
# ============================================================================

# Set up all the useful components of the necessary calculation
singleTraditionalPage <- templateSize + 
                         (itemsPerPage * (dataTemplateSize+dataItemSize))
firstFlyingPage <- templateSize + 
                   dataTemplateSize + 
                   (itemsPerPage * dataItemSize)
nthFlyingPage <- itemsPerPage * dataItemSize
firstSyncKitPage <- firstFlyingPage

expectedNewItems <- function(rate) {
    return(1/rate)
}

nthSyncKitPage <- function(rate) {
    # We have access to the outside scope here
    # dataItemSize binds correctly to the value above
    return(expectedNewItems(rate) * dataItemSize)
}

# Now we'll generate the series
points <- seq(from=scaleMin,to=scaleMax,length=20)
traditional <- rep(singleTraditionalPage, length(points))
flying <- rep(nthFlyingPage, length(points))
flying[1] <- firstFlyingPage
syncKit <- nthSyncKitPage(points)
syncKit[1] <- firstSyncKitPage

bandwidthTable = data.frame(
    traditional=traditional,
    flying=flying,
    syncKit=syncKit
)

#
plot_colors <- c(rgb(r=0.0,g=0.0,b=0.9), "red", "forestgreen")

# Start PDF device driver to save output to figure.pdf
pdf(file="theoretical_bandwidth.pdf", height=3.5, width=5)

# Trim off excess margin space (bottom, left, top, right)par(mar=c(4.2, 3.8, 0.2, 0.2))
par(mar=c(4.2, 3.8, 0.2, 0.2))

# Graph autos using a y axis that uses the full range of value
# in autos_data. Label axes with smaller font and use larger 
# line widths.
plot(bandwidthTable$traditional, 
    type="l", 
    col=plot_colors[1], 
    ylim=range(bandwidthTable), 
    axes=F, 
    ann=T, 
    xlab="Visit Frequency",
    ylab="Average Bandwidth", 
    cex.lab=0.8, 
    lwd=2
)

# Make x axis tick marks without labels
axis(1, lab=F)


# Plot y axis with smaller horizontal labels 
axis(1, at=points[seq(7, length(points), 7)], lab=points[seq(7, length(points), 7)])
axis(2, las=1, cex.axis=0.8)


# Create box around plot
box()

# Graph trucks with thicker red dashed line
lines(bandwidthTable$flying, type="l", lty=2, lwd=2, col=plot_colors[2])

# Graph suvs with thicker green dotted line
lines(bandwidthTable$syncKit, type="l", lty=3, lwd=2, col=plot_colors[3])

# Create a legend in the top-left corner that is slightly  
# smaller and has no border
legend("topleft", c("Traditional", "Flying Templates", "SyncKit"), cex=0.8, col=plot_colors, 
   lty=1:3, lwd=2, bty="n");
  
# Turn off device driver (to flush output to PDF)
dev.off()

# Restore default margins
par(mar=c(5, 4, 4, 2) + 0.1)
