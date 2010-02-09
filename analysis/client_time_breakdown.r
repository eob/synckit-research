# ============================================================================
# PLOT 1
# Create a stacked bar of the time spent
# ----------------------------------------------------------------------------
# Parameters
#
dataFile <- "monday_night.csv"
test <- "Feb 2"
page <- "Blog"
# ============================================================================
#
# The file looks like this
#
#  test,page,strategy,visitnumber,ttr,datafetch,databulkload,templateparse,latency,bandwidth,date
#  Feb 2,Blog,Sync Kit,1,377,232,16,15,1,1,2010-02-01 21:03:34.337516-05
#
#

data <- read.csv(dataFile,
                header=T,
                dec='.',
                na.strings=c('XXXXXXX')
)

# pdf(file="client_time_breakdown.pdf", height=3.5, width=5)

# Filter the table for only rows where the frequency count was 1
# NOTE: In real data set, should also filter for other things, like 
# test and page
filtered <- data[data$test == test,]      
filtered <- data[data$page == page,]      

# Add new column equal to everything left over from TTR
filtered["wire"] = filtered$ttr - filtered$datafetch - filtered$databulkload - filtered$templateparse

# Average the data across each strategy
filteredAgg <- aggregate(filtered, 
                        by=list(filtered$strategy), 
                        FUN=mean, 
                        na.rm=TRUE)

# Note: Group.1 is the name of the aggregation bucket. 
# It would be nice if we could rename this in the 
# aggregate params back to "strategy"
toGraph <- filteredAgg[c("Group.1", "wire", "datafetch", "databulkload", "templateparse")]
colnames(toGraph)[2] <- "Wire"
colnames(toGraph)[3] <- "Server"
colnames(toGraph)[4] <- "Client DB"
colnames(toGraph)[5] <- "Template"


# We have to set the DOM Load manually, since we measured this manually
# Wiki:
# FT    114.4082155
# SyncKit   118.7076748
# Trad. 100
# Blog
#   DOM Load
# FT    99.50463822
# SyncKit   102.4118738
# Trad. 80
toGraph["DOM Load"] = c(114, 118, 100)

# We have to set the DOM Load manually, since we measured this manually

print(toGraph)
print(names(toGraph))

# Expand right side of clipping rect to make room for the legend
par(xpd=T,  # Clip plotting to the figure region, rather than the device region
    mar=par()$mar+c(0,0,0,0.1) # Move out the right-hand margin by 10 lines
    )

# Plot them in a stacked bar
# data.matrix converts the data frame into a matrix
# We only extract colums 2-4 because col1 is the strategy name
# We use the transposed column 1 for the names in the argument below
barplot(t(data.matrix(toGraph[2:6])), 
        main="Client-side Time", 
        ylab="Total Time (ms)", 
        col=rainbow(length(colnames(toGraph))),
        space=0.1, 
        cex.axis=0.8, 
        las=1,
        names.arg=toGraph$Group.1, # Group.1 is the name of the strategy 
        cex=0.8)

# Legend
# The first arg is the x position -- in this case one category past the 
# number of styles.
# The second arg is the y position. In this case, we'll make it the top
bar_parts <- names(toGraph[2:6])


legend(length(toGraph$Group.1), 200, bar_parts, cex=0.8, fill=rainbow(length(colnames(toGraph))));


