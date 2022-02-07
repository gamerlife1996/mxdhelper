tesseract chi_my.font.exp0.tif chi_my.font.exp0 --psm 7 nobatch box.train

unicharset_extractor chi_my.font.exp0.box

mftraining -F font_properties -U unicharset -O chi_my.unicharset chi_my.font.exp0.tr
cntraining chi_my.font.exp0.tr

ren inttemp chi_my.inttemp
ren pffmtable chi_my.pffmtable
ren normproto chi_my.normproto
ren shapetable chi_my.shapetable

combine_tessdata chi_my.