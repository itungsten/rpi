# magic
the project of magic album

### viewer
viewer是程序主界面，类似一个相簿

### classifier
classifier就是一个判断用户操作类型的分类器。
用户在手势操作时，会由viewer程序生成一张手势图，由classifier打上类型标签

### transformer
如果classifier的结果是动态化，将由transformer进行转化为gif
