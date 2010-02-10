# ============================================================================
# PLOT 1
# Create a stacked bar of the time spent
# ----------------------------------------------------------------------------
# Parameters
#
#dataFile <- "breakdown_test.csv"
#test <- "Feb 2"
dataFile <- "combined-output.csv"
test <- "Test"
page <- "Wiki"
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

pdf(file="client_time_breakdown.pdf", height=3.5, width=5)

# ----------------------------------------------------------------------------
# FILTER THE DATA SET FOR ONLY THE SPECIFIED TEST AND PAGE
# ----------------------------------------------------------------------------

#filtered <- data[data$test == test,]      
filtered <- data[data$page == page,]      

# Average the data across each strategy
filteredAgg <- aggregate(filtered, 
                        by=list(filtered$strategy), 
                        FUN=mean, 
                        na.rm=TRUE)

# Note: Group.1 is the name of the aggregation bucket. 
# It would be nice if we could rename this in the 
# aggregate params back to "strategy"
toGraph <- filteredAgg[c("Group.1", "datafetch", "databulkload", "templateparse", "ttr")]
colnames(toGraph)[1] <- "Strategy"
colnames(toGraph)[2] <- "DataFetch"
colnames(toGraph)[3] <- "Client DB"
colnames(toGraph)[4] <- "Template"
colnames(toGraph)[5] <- "TTR"

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# DOM LOAD
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------

if (page == "Blog") {
    # The Blog
    toGraph[toGraph$Strategy == 'Traditional',"DOM Load"] = 80
    toGraph[toGraph$Strategy == 'Flying Templates',"DOM Load"] = 99.504
    toGraph[toGraph$Strategy == 'Sync Kit',"DOM Load"] = 102.411
} else {
    # The Wiki
    toGraph[toGraph$Strategy == 'Traditional',"DOM Load"] = 100
    toGraph[toGraph$Strategy == 'Flying Templates',"DOM Load"] = 114.408
    toGraph[toGraph$Strategy == 'Sync Kit',"DOM Load"] = 118.7
}

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ROUND TRIP TIME
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
#
# The net RTT numbers are manually inserted to provide comparison to what the
# network latency is
#
# ----------------------------------------------------------------------------

toGraph["Net RTT"] = c(3,3,3)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# SERVER TIME
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
#
# We have to calculate the server time differently for each strategy. 
# - For SK and Flying, it is the average of the data fetch times minus the RTT
#    * Note that this is slightly wrong: it does not take into account the
#    * occasional transfer of the HTML template that occurs on first visit
# - For Traditional, it is the TTR - RTT - DOMLoad
# ----------------------------------------------------------------------------

toGraph[toGraph$Strategy == 'Sync Kit',"Server"] = 
    toGraph[toGraph$Strategy == 'Sync Kit',"DataFetch"] -
    toGraph[toGraph$Strategy == 'Sync Kit',"Net RTT"]

toGraph[toGraph$Strategy == 'Flying Templates',"Server"] = 
    toGraph[toGraph$Strategy == 'Flying Templates',"DataFetch"] -
    toGraph[toGraph$Strategy == 'Flying Templates',"Net RTT"]

toGraph[toGraph$Strategy == 'Traditional',"Server"] = 
    toGraph[toGraph$Strategy == 'Traditional',"TTR"] -
    toGraph[toGraph$Strategy == 'Traditional',"Net RTT"] -
    toGraph[toGraph$Strategy == 'Traditional',"DOM Load"]


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# LEFT OVERS
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
#
# The TTR value is the entire measured time from beginning to end of the page
# load. 
#
# ----------------------------------------------------------------------------

filtered["leftover"] = filtered$ttr - 
                          filtered$Server - 
                          filtered$"Client DB" - 
                          filtered$Template -
                          filtered$"Net RTT"

# ----------------------------------------------------------------------------
# SETUP AND DO BAR GRAPH
# ----------------------------------------------------------------------------

toGraph <- toGraph[c("Strategy", "DOM Load", "Server", "Net RTT", "Client DB", "Template")]


# Expand right side of clipping rect to make room for the legend
par(xpd=T,  # Clip plotting to the figure region, rather than the device region
    mar=par()$mar+c(0,0,0,5) # Move out the right-hand margin by 10 lines
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
        names.arg=toGraph$Strategy, # Group.1 is the name of the strategy 
        cex=0.8)

# Legend
# The first arg is the x position -- in this case one category past the 
# number of styles.
# The second arg is the y position. In this case, we'll make it the top
bar_parts <- names(toGraph[2:6])

legend(length(toGraph$Strategy)+0.4, 200, bar_parts, cex=0.8, fill=rainbow(length(colnames(toGraph))))

# Turn off device driver (to flush output to PDF)
dev.off()

# Restore default margins
par(mar=c(5, 4, 4, 2) + 0.1)
