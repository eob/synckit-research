import sys

handled = {}
max_num = 0

print "handled"

for line in open(sys.argv[1]):
    nums = line.replace(":","").split()
    nums[0] = int(nums[0])
    handled[nums[0]] = "a"
    max_num = max(max_num, nums[0])
    for num in nums[1:]:
        num = int(num)
        handled[num] = "a"
        max_num = max(max_num, num)
        print "%d %d" % (nums[0], num)

print "not handled"

for i in xrange(num):
    if i not in handled:
        print i
