#Requires AutoHotkey v2.0-beta
#Singleinstance
; Enters words into squardle.
; last updated 04/08/2023
; Developer: Hugo Burton

; Set delay values (in milliseconds)
letterDelay := 25
wordDelay := 300

; Get the path to the script directory
scriptDir := A_ScriptDir
; Combine the script directory with the filename
filePath := scriptDir . "\squardlewords.txt"


^+h::{
    ; Check if the file exists
    if !FileExist(filePath) {
        MsgBox "File not found: " . filePath
        ExitApp
    }

    ; Read the contents of the file
    words := FileRead(filePath)

    words := StrSplit(words, "\n")

    ; Loop through each word
    for index, word in words {
        ; Loop through each letter in the word
        wordLength := StrLen(word)

        Loop wordLength -1 {
            ; Type each letter with a delay
            Send SubStr(word, A_Index, 1)
            Sleep letterDelay
        }

        ; Press Enter and wait for wordDelay milliseconds
        Send "{Enter}"
        Sleep wordDelay
    }

    MsgBox "Script completed"

}

; Pause key in case of emergency
Pause::
{
	Pause -1
}

