
# ============================================================================
# FIGURE 8
# Create bar graphs of throughput and bandwidth on the wiki
# ** NOTE: This averages across all test files (different frequencies per day)
#          for a given strategy
# ----------------------------------------------------------------------------
# Parameters

#synckitPercentageCached <- 0.3 # The percent of SyncKit served pages that were cached
dataFileName <- "wiki-server-rates.txt"

#
# file,highest_rate,attempted_rate,avg_data
# test_freq_12_per_day_traditional.txt,133.600000,135,159456.000000
# test_freq_2_per_day_tokyo.txt,226.200000,193,61086.000000
# test_freq_24_per_day_synckit.txt,580.500000,503,13365.000000
#
# ============================================================================

#synckitThroughputMultiplier <- 1/(1-synckitPercentageCached)

tp <- read.csv(dataFileName,
    header=T,
    dec='.',
    na.strings=c('XXXXXXX')
)

# Aggregate across all the merged CSV file (this file should contain all 3)

# Average the data across each strategy
agg <- aggregate(tp, 
                   by=list(tp$strategy), 
                   FUN=mean, 
                   na.rm=TRUE)

plotColors <- c(rgb(r=0.0,g=0.0,b=0.9), "red", "forestgreen")

# Multiply the throughput for SyncKit by the multiplier. This is because we 
# treat throughput for SyncKit as "clients served" rather than "pages served" since
# some of the pages "served" never actually result in an HTTP request.
# Group.1 is the strategy because it was aggregated
#agg[agg$Group.1 == "Sync Kit","highest_rate"] <- agg[agg$Group.1 == "Sync Kit","highest_rate"]  * synckitThroughputMultiplier

pdf(file="figure_8a_wiki_throughput.pdf", height=3.5, width=5)

graphPoints <- barplot(agg$"highest_rate", 
    main="Wiki Throughput",    
    ylab="Pages / Second",
    names.arg=agg$Group.1,
    col=plotColors
)
text(graphPoints, agg$"highest_rate", agg$"highest_rate")

dev.off()

pdf(file="figure_8b_wiki_bandwidth.pdf", height=3.5, width=5)

barplot(agg$"avg_data"/1024, 
    main="Wiki Bandwidth",    
    ylab="KB / Request",
    names.arg=agg$Group.1,
    col=plotColors
)

dev.off()
