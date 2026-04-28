# AndroidWorld 任务清单（中英对照 + 远程真机可跑性）

**可跑性**：Y=容易跑（系统自带）｜ P=可跑但需装 app 或人工判分｜ F=难跑（依赖 SQLite 预置 / adb 判分）

**总计**：91 个任务

## composite/markor_sms

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| MarkorCreateNoteAndSms |  | P | 1.8 | 在 Markor 创建指定名字/内容的笔记，然后通过 Simple SMS Messenger 把笔记内容发短信给指定号码。 |

<details><summary>英文 goal 模板</summary>

- **MarkorCreateNoteAndSms**: Create a new note in Markor named {file_name} with the following text: {text}. Share the entire content of the note with the phone number {number} via SMS using Simple SMS Messenger

</details>

## composite/system

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| TurnOffWifiAndTurnOnBluetooth |  | Y | 2 | 先关闭 WiFi，然后打开蓝牙。 |
| TurnOnWifiAndOpenApp |  | Y | 2 | 先打开 WiFi，然后打开 {app_name} 应用。 |

<details><summary>英文 goal 模板</summary>

- **TurnOffWifiAndTurnOnBluetooth**: Turn off WiFi, then enable bluetooth
- **TurnOnWifiAndOpenApp**: Turn on Wifi, then open the {app_name} app

</details>

## single/audio_recorder

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| AudioRecorderRecordAudio |  | P | 1.2 | 用 Audio Recorder 应用录一段音频并保存。 |
| AudioRecorderRecordAudioWithFileName |  | P | 2 | 用 Audio Recorder 录一段音频，保存时命名为 "{file_name}"。 |

<details><summary>英文 goal 模板</summary>

- **AudioRecorderRecordAudio**: Record an audio clip using Audio Recorder app and save it.
- **AudioRecorderRecordAudioWithFileName**: Record an audio clip and save it with name "{file_name}" using Audio Recorder app.

</details>

## single/browser

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| BrowserDraw |  | F | - | 在文件管理器 Downloads 中打开 task.html（用 Chrome 打开），然后用顶部显示的三种颜色在画布上作画并提交。 |
| BrowserMaze |  | F | - | 在文件管理器 Downloads 中打开 task.html（用 Chrome 打开），通过方向按钮把 X 移动到右下角单元格。 |
| BrowserMultiply |  | F | 2.2 | 在文件管理器 Downloads 中打开 task.html（用 Chrome 打开），点击按钮 5 次记下显示的数字，把它们的乘积填入表单。 |

<details><summary>英文 goal 模板</summary>

- **BrowserDraw**: Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then create a drawing using the three colors shown at the top and hit submit.
- **BrowserMaze**: Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then navigate the X to the bottom-right cell, by using the direction buttons.
- **BrowserMultiply**: Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then click the button 5 times, remember the numbers displayed, and enter their product in the form.

</details>

## single/calendar

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| SimpleCalendarAddOneEvent |  | P | 3.4 | 在日历添加事件（单个，指定日期时间/标题/描述/地点）。 |
| SimpleCalendarAddOneEventInTwoWeeks |  | P | 3.4 | 在日历里给两周后的某天添加一个事件。 |
| SimpleCalendarAddOneEventRelativeDay |  | P | 3.4 | 在日历里给相对某天（例如明天 / 本周五）添加一个事件。 |
| SimpleCalendarAddOneEventTomorrow |  | P | 3.4 | 在日历里给明天添加一个事件。 |
| SimpleCalendarAddRepeatingEvent |  | P | 3.4 | 在日历里添加一个周期性重复事件。 |
| SimpleCalendarDeleteEvents |  | F | 1.4 | 在日历里按条件删除一组事件。 |
| SimpleCalendarDeleteEventsOnRelativeDay |  | F | 1.2 | 在日历里删除某个相对日期当天的全部事件。 |
| SimpleCalendarDeleteOneEvent |  | F | 1.2 | 在日历里删除指定的一个事件。 |

<details><summary>英文 goal 模板</summary>

- **SimpleCalendarAddOneEvent**: In Simple Calendar Pro, create a calendar event on {year}-{month}-{day} at {hour}h with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.
- **SimpleCalendarAddOneEventInTwoWeeks**: In Simple Calendar Pro, create a calendar event in two weeks from today at {hour}h with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.
- **SimpleCalendarAddOneEventRelativeDay**: In Simple Calendar Pro, create a calendar event for this {day_of_week} at {hour}h with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.
- **SimpleCalendarAddOneEventTomorrow**: In Simple Calendar Pro, create a calendar event for tomorrow at {hour}h with the title '{event_title}' and the description '{event_description}'. The event should last for {duration_mins} mins.
- **SimpleCalendarAddRepeatingEvent**: In Simple Calendar Pro, create a recurring calendar event titled '{event_title}' starting on {year}-{month}-{day} at {hour}h. The event recurs {repeat_rule}, forever, and lasts for {duration_mins} minutes each occurrence. The event description should be '{event_description}'.
- **SimpleCalendarDeleteEvents**: In Simple Calendar Pro, delete all the calendar events on {year}-{month}-{day}
- **SimpleCalendarDeleteEventsOnRelativeDay**: In Simple Calendar Pro, delete all events scheduled for this {day_of_week}.
- **SimpleCalendarDeleteOneEvent**: In Simple Calendar Pro, delete the calendar event on {year}-{month}-{day} at {hour}h with the title '{event_title}'

</details>

## single/camera

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| CameraTakePhoto |  | Y | 1 | 用相机拍一张照片。 |
| CameraTakeVideo |  | Y | 1 | 用相机录一段视频。 |

<details><summary>英文 goal 模板</summary>

- **CameraTakePhoto**: Take one photo.
- **CameraTakeVideo**: Take one video.

</details>

## single/clock

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| ClockStopWatchPausedVerify |  | Y | 1 | 打开时钟的秒表并确保它处于暂停状态。 |
| ClockStopWatchRunning |  | Y | 1 | 在时钟应用里启动秒表。 |
| ClockTimerEntry |  | Y | 1 | 在时钟里设置一个倒计时（指定时分秒）。 |

<details><summary>英文 goal 模板</summary>

- **ClockStopWatchPausedVerify**: Pause the stopwatch.
- **ClockStopWatchRunning**: Run the stopwatch.
- **ClockTimerEntry**: Create a timer with {hours} hours, {minutes} minutes, and {seconds} seconds. Do not start the timer.

</details>

## single/contacts

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| ContactsAddContact |  | Y | 1.2 | 新建一个联系人 {name}，电话 {number}。 |
| ContactsNewContactDraft |  | Y | 1.2 | 在通讯录里打开新建联系人页面并填入 {name}/{number}（不保存，只留草稿）。 |

<details><summary>英文 goal 模板</summary>

- **ContactsAddContact**: Create a new contact for {name}. Their number is {number}.
- **ContactsNewContactDraft**: Go to the new contact screen and enter the following details: First Name: {first}, Last Name: {last}, Phone: {phone}, Phone Label: {phone_label}. Do NOT hit save.

</details>

## single/expense

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| ExpenseAddMultiple |  | F | 6 | 在 Pro Expense 应用中添加给出的多条支出（通常 3 条）。 |
| ExpenseAddMultipleFromGallery |  | F | 6 | 把相册里发票图片中的支出信息添加到 Pro Expense 应用。 |
| ExpenseAddMultipleFromMarkor |  | F | 6 | 把 Markor 里 expenses.txt 中的支出添加到 Pro Expense 应用。 |
| ExpenseAddSingle |  | P | 1.2 | 在 Pro Expense 应用中添加给出的一条支出。 |
| ExpenseDeleteDuplicates |  | F | - | 在 Pro Expense 中删除所有完全重复的支出，每组只保留一条。 |
| ExpenseDeleteDuplicates2 |  | F | 1.8 | 同上，但噪声条目更多（约 40 条）。 |
| ExpenseDeleteMultiple |  | F | 2 | 在 Pro Expense 中删除给定名字的 3 条支出。 |
| ExpenseDeleteMultiple2 |  | F | 3.4 | 在 Pro Expense 中删除给定名字的 3 条支出（另有 50 条噪声）。 |
| ExpenseDeleteSingle |  | F | 1 | 在 Pro Expense 中删除给定名字的 1 条支出。 |

<details><summary>英文 goal 模板</summary>

- **ExpenseAddMultiple**: Add the following expenses into the pro expense app: <N 条支出的清单（name/amount/category/note）>
- **ExpenseAddMultipleFromGallery**: Add the expenses from the pictures of receipts in the gallery to the pro expense app.
- **ExpenseAddMultipleFromMarkor**: Add the expenses from expenses.txt in Markor to the pro expense app.
- **ExpenseAddSingle**: Add the following expenses into the pro expense app: <1 条支出>
- **ExpenseDeleteDuplicates**: Delete all but one of any expenses in pro expense that are exact duplicates, ensuring at least one instance of each unique expense remains.
- **ExpenseDeleteDuplicates2**: Delete all but one of any expenses in pro expense that are exact duplicates (harder, more noise).
- **ExpenseDeleteMultiple**: Delete the following expenses from pro expense: <3 条支出名称列表>.
- **ExpenseDeleteMultiple2**: Delete the following expenses from pro expense: <3 条支出，另有 50 条噪声>.
- **ExpenseDeleteSingle**: Delete the following expenses from pro expense: <1 条支出>.

</details>

## single/files

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| FilesDeleteFile |  | P | 2.2 | 在 Files 文件管理器中删除指定文件。 |
| FilesMoveFile |  | P | 2 | 在 Files 文件管理器中把指定文件移动到另一个目录。 |

<details><summary>英文 goal 模板</summary>

- **FilesDeleteFile**: Delete the file {file_name} from the Android filesystem located in the {subfolder} folder within the sdk_gphone_x86_64 storage area.
- **FilesMoveFile**: Move the file {file_name} from {source_folder} within the sdk_gphone_x86_64 storage area to the {destination_folder} within the same sdk_gphone_x86_64 storage area in the Android filesystem.

</details>

## single/markor

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| MarkorAddNoteHeader |  | P | 1.2 | 在 Markor 的某个笔记顶部添加一段标题/前言。 |
| MarkorChangeNoteContent |  | P | 1.2 | 修改 Markor 某个笔记的内容。 |
| MarkorCreateFolder |  | P | 1 | 在 Markor 里创建一个名为 {folder_name} 的新文件夹。 |
| MarkorCreateNote |  | P | 1.6 | 在 Markor 里新建笔记（指定文件名和内容）。 |
| MarkorCreateNoteFromClipboard |  | P | 1.4 | 把剪贴板内容作为笔记内容，在 Markor 里新建笔记。 |
| MarkorDeleteAllNotes |  | P | 1.4 | 删除 Markor 中所有的笔记。 |
| MarkorDeleteNewestNote |  | P | 1 | 删除 Markor 中最新的那条笔记。 |
| MarkorDeleteNote |  | P | 1 | 删除 Markor 中名为 {file_name} 的笔记。 |
| MarkorEditNote |  | P | 1.2 | 编辑 Markor 中的 {file_name}：在顶部/底部加文字 或 替换全文。 |
| MarkorMergeNotes |  | P | 7.8 | 把 Markor 的多个笔记合并成一个。 |
| MarkorMoveNote |  | P | 1.4 | 把 Markor 中的某个笔记移动到另一个文件夹。 |
| MarkorTranscribeReceipt |  | P | 1.8 | 把一张小票图片里的内容在 Markor 中转写成笔记。 |
| MarkorTranscribeVideo |  | P | 2 | 把一段视频里的内容在 Markor 中转写成笔记。 |

<details><summary>英文 goal 模板</summary>

- **MarkorAddNoteHeader**: Update the Markor note {original_name} by adding the following text, along with a new blank line before the existing content: "{header}", and rename it to {new_name}.
- **MarkorChangeNoteContent**: Update the content of {original_name} to "{updated_content}" in Markor and change its name to {new_name}.
- **MarkorCreateFolder**: Create a new folder in Markor named {folder_name}.
- **MarkorCreateNote**: Create a new note in Markor named {file_name} with the following text: {text}
- **MarkorCreateNoteFromClipboard**: Create a note in Markor named {file_name}. Perform a paste operation in the note and save the note.
- **MarkorDeleteAllNotes**: Delete all my notes in Markor.
- **MarkorDeleteNewestNote**: Delete the newest note in Markor.
- **MarkorDeleteNote**: Delete the note in Markor named {file_name}.
- **MarkorEditNote**: Edit {file_name} in Markor. 编辑类型三选一：在顶部添加 {header} / 在底部添加 {footer} / 用 {replace_text} 替换全文。
- **MarkorMergeNotes**: Merge the contents of Markor notes {file1_name}, {file2_name} and {file3_name} (in the same order) into a new Markor note named {new_file_name} and save it. Add a new line between the content of each note.
- **MarkorMoveNote**: In Markor, move the note {file_name} from {source_folder} to {destination_folder}.
- **MarkorTranscribeReceipt**: Create a file in Markor, called receipt.md with the transactions from the receipt.png. Use Simple Gallery to view the receipt. Please enter transactions in csv format including the header "Date, Item, Amount".
- **MarkorTranscribeVideo**: Transcribe the contents of video {video_name} by watching it in VLC player (located in Download) and writing the sequence of strings shown on each frame to the text file {file_name} in Markor as a comma separated list. For example, if the first frame shows the text "edna" and the second frame shows the text "pineapple", then the text file should contain only the following text: "edna, pineapple".

</details>

## single/osmand

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| OsmAndFavorite |  | P | 1.3 | 在 OsmAnd 地图应用中把 {location} 加入收藏。 |
| OsmAndMarker |  | P | 2.0 | 在 OsmAnd 地图应用中为 {location} 添加一个标记。 |
| OsmAndTrack |  | P | 12 | 在 OsmAnd 中创建一条多点途经的路线/轨迹（Track）。 |

<details><summary>英文 goal 模板</summary>

- **OsmAndFavorite**: Add a favorite location marker for {location} in the OsmAnd maps app.
- **OsmAndMarker**: Add a location marker for {location} in the OsmAnd maps app.
- **OsmAndTrack**: Save a track with waypoints {…} in the OsmAnd maps app in the same order as listed.

</details>

## single/recipe

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| RecipeAddMultipleRecipes |  | F | 6 | 在 Broccoli 食谱应用中添加给出的多份食谱。 |
| RecipeAddMultipleRecipesFromImage |  | F | 6 | 把相册图片里的食谱信息添加到 Broccoli 应用。 |
| RecipeAddMultipleRecipesFromMarkor |  | F | 6 | 把 Markor 里 recipes.txt 中的食谱添加到 Broccoli 应用。 |
| RecipeAddMultipleRecipesFromMarkor2 |  | F | 6 | 把 Markor 里分散的多个食谱笔记添加到 Broccoli 应用。 |
| RecipeAddSingleRecipe |  | P | 2.4 | 在 Broccoli 食谱应用中添加给出的一份食谱。 |
| RecipeDeleteDuplicateRecipes |  | F | 1 | 在 Broccoli 中删除所有完全重复的食谱，每组只保留一条。 |
| RecipeDeleteDuplicateRecipes2 |  | F | 2.4 | 同上，但噪声数量更大。 |
| RecipeDeleteDuplicateRecipes3 |  | F | 3.4 | 同上，噪声数量很大且需要滚动才能看到。 |
| RecipeDeleteMultipleRecipes |  | F | 2.4 | 在 Broccoli 中删除给定名字的 3 份食谱。 |
| RecipeDeleteMultipleRecipesWithConstraint |  | F | 4 | 在 Broccoli 中删除做法里含 {ingredient} 的所有食谱。 |
| RecipeDeleteMultipleRecipesWithNoise |  | F | 3.4 | 删除指定 3 份食谱（另有 29 条噪声）。 |
| RecipeDeleteSingleRecipe |  | F | 1 | 在 Broccoli 中删除 1 份指定食谱。 |
| RecipeDeleteSingleWithRecipeWithNoise |  | F | 2 | 删除指定 1 份食谱（另有 29 条噪声）。 |

<details><summary>英文 goal 模板</summary>

- **RecipeAddMultipleRecipes**: Add the following recipes into the Broccoli app: <3 份随机食谱>.
- **RecipeAddMultipleRecipesFromImage**: Add the recipes from the pictures in the gallery to the Broccoli app.
- **RecipeAddMultipleRecipesFromMarkor**: Add the recipes from recipes.txt in Markor to the Broccoli recipe app.
- **RecipeAddMultipleRecipesFromMarkor2**: Add the recipes from all recipe notes (*.md) in Markor to the Broccoli app.
- **RecipeAddSingleRecipe**: Add the following recipes into the Broccoli app: <1 份食谱>.
- **RecipeDeleteDuplicateRecipes**: Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains
- **RecipeDeleteDuplicateRecipes2**: Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains
- **RecipeDeleteDuplicateRecipes3**: Delete all but one of any recipes in the Broccoli app that are exact duplicates (大量噪声，需滚动).
- **RecipeDeleteMultipleRecipes**: Delete the following recipes from Broccoli app: <3 个食谱名>.
- **RecipeDeleteMultipleRecipesWithConstraint**: Delete the recipes from Broccoli app that use {…} in the directions.
- **RecipeDeleteMultipleRecipesWithNoise**: Delete the following recipes from Broccoli app: <3 个食谱名，另有 29 条噪声>.
- **RecipeDeleteSingleRecipe**: Delete the following recipes from Broccoli app: <1 个食谱>.
- **RecipeDeleteSingleWithRecipeWithNoise**: Delete the following recipes from Broccoli app: <1 个食谱，29 条噪声>.

</details>

## single/retro_music

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| RetroCreatePlaylist |  | P | 2.4 | 在 Retro Music 里创建一个播放列表并加入指定歌曲。 |
| RetroPlayingQueue |  | P | 3.2 | 在 Retro Music 中把指定歌曲加入当前播放队列。 |
| RetroPlaylistDuration |  | F | 3 | 在 Retro Music 里创建一个总时长符合约束的播放列表。 |
| RetroSavePlaylist |  | P | 5 | 在 Retro Music 里保存/导出一个指定的播放列表。 |

<details><summary>英文 goal 模板</summary>

- **RetroCreatePlaylist**: Create a playlist in Retro Music titled "{…}" with the following songs, in order: {…}
- **RetroPlayingQueue**: Add the following songs, in order, {…} to my playing queue in Retro music.
- **RetroPlaylistDuration**: Create a playlist in Retro Music titled "{…}" with a duration between 45 and 50 minutes using the provided songs.
- **RetroSavePlaylist**: Create a playlist in Retro Music titled "{…}" with the following songs, in order: {…}. Then export the playlist to the Downloads directory on the device.

</details>

## single/simple_draw_pro

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| SimpleDrawProCreateDrawing |  | P | 1.8 | 在 Simple Draw Pro 里创建一幅画（指定颜色/形状）。 |

<details><summary>英文 goal 模板</summary>

- **SimpleDrawProCreateDrawing**: Create a new drawing in Simple Draw Pro. Name it {file_name}. Save it in the Pictures folder within the sdk_gphone_x86_64 storage area.

</details>

## single/simple_gallery_pro

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| SaveCopyOfReceiptTaskEval |  | P | 1.6 | 在 Simple Gallery Pro 里把指定小票图片另存一份副本。 |

<details><summary>英文 goal 模板</summary>

- **SaveCopyOfReceiptTaskEval**: In Simple Gallery Pro, copy {file_name} in DCIM and save a copy with the same name in Download

</details>

## single/sms

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| SimpleSmsReply |  | F | 1.2 | 用 Simple SMS Messenger 回复指定号码的短信，回复内容给定。 |
| SimpleSmsReplyMostRecent |  | F | - | 用 Simple SMS Messenger 回复最近一条收到的短信。 |
| SimpleSmsResend |  | F | 1.2 | 在 Simple SMS Messenger 里重发上一条发送失败的短信。 |
| SimpleSmsSend |  | P | - | 用 Simple SMS Messenger 给指定号码发送指定内容的短信。 |
| SimpleSmsSendClipboardContent |  | P | 1.2 | 用 Simple SMS Messenger 把剪贴板当前内容发送给指定号码。 |
| SimpleSmsSendReceivedAddress |  | F | 1.8 | 把最近收到的短信里的地址通过短信转发给另一个号码。 |

<details><summary>英文 goal 模板</summary>

- **SimpleSmsReply**: Reply to {number} with message: {message} in Simple SMS Messenger
- **SimpleSmsReplyMostRecent**: Reply to the most recent text message using Simple SMS Messenger with message: {message}
- **SimpleSmsResend**: Resend the message I just sent to {name} in Simple SMS Messenger
- **SimpleSmsSend**: Send a text message using Simple SMS Messenger to {number} with message: {message}
- **SimpleSmsSendClipboardContent**: Send a message to {number} with the clipboard content in Simple SMS Messenger
- **SimpleSmsSendReceivedAddress**: Text the address of the event to {name1} that {name2} just sent me in Simple SMS Messenger

</details>

## single/system

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| OpenAppTaskEval |  | Y | 1 | 打开 {app_name} 应用。 |
| SystemBluetoothTurnOff |  | Y | 1 | 把蓝牙关闭。 |
| SystemBluetoothTurnOffVerify |  | Y | 1 | 把蓝牙关闭（设置里确认）。 |
| SystemBluetoothTurnOn |  | Y | 1 | 把蓝牙打开。 |
| SystemBluetoothTurnOnVerify |  | Y | 1 | 把蓝牙打开（设置里确认）。 |
| SystemBrightnessMax |  | Y | 1 | 把屏幕亮度调到最大。 |
| SystemBrightnessMaxVerify |  | Y | 1 | 把屏幕亮度调到最大（设置里确认）。 |
| SystemBrightnessMin |  | Y | 1 | 把屏幕亮度调到最小。 |
| SystemBrightnessMinVerify |  | Y | 1 | 把屏幕亮度调到最小（设置里确认）。 |
| SystemCopyToClipboard |  | Y | 1 | 把以下文本复制到剪贴板：{clipboard_content}。 |
| SystemWifiTurnOff |  | Y | 1 | 关闭 WiFi。 |
| SystemWifiTurnOffVerify |  | Y | 1 | 关闭 WiFi（设置里确认）。 |
| SystemWifiTurnOn |  | Y | 1 | 打开 WiFi。 |
| SystemWifiTurnOnVerify |  | Y | 1 | 打开 WiFi（设置里确认）。 |

<details><summary>英文 goal 模板</summary>

- **OpenAppTaskEval**: Open the {app_name} app. Clear any pop-ups that may appear by granting all permissions that are required.
- **SystemBluetoothTurnOff**: Turn bluetooth {on_or_off}.
- **SystemBluetoothTurnOffVerify**: Turn bluetooth {on_or_off}.
- **SystemBluetoothTurnOn**: Turn bluetooth {on_or_off}.
- **SystemBluetoothTurnOnVerify**: Turn bluetooth {on_or_off}.
- **SystemBrightnessMax**: Turn brightness to the {max_or_min} value.
- **SystemBrightnessMaxVerify**: Turn brightness to the {max_or_min} value.
- **SystemBrightnessMin**: Turn brightness to the {max_or_min} value.
- **SystemBrightnessMinVerify**: Turn brightness to the {max_or_min} value.
- **SystemCopyToClipboard**: Copy the following text to the clipboard: {clipboard_content}
- **SystemWifiTurnOff**: Turn wifi {on_or_off}.
- **SystemWifiTurnOffVerify**: Turn wifi {on_or_off}.
- **SystemWifiTurnOn**: Turn wifi {on_or_off}.
- **SystemWifiTurnOnVerify**: Turn wifi {on_or_off}.

</details>

## single/vlc

| # | 任务名 | 可跑 | 复杂度 | 中文描述 |
|---|---|---|---|---|
| VlcCreatePlaylist |  | P | 2.8 | 在 VLC 里创建一个播放列表并加入指定媒体。 |
| VlcCreateTwoPlaylists |  | P | 4.8 | 在 VLC 里创建两个不同的播放列表。 |

<details><summary>英文 goal 模板</summary>

- **VlcCreatePlaylist**: Create a playlist titled "{…}" with the following files in VLC (located in Internal Memory/VLCVideos), in order: {…}
- **VlcCreateTwoPlaylists**: {…}. And then, {…}.

</details>

## 快速索引（编号 → 任务名）

1. [F] BrowserDraw — 在文件管理器 Downloads 中打开 task.html（用 Chrome 打开），然后用顶部显示的三种颜色在画布上作画并提交。
2. [F] BrowserMaze — 在文件管理器 Downloads 中打开 task.html（用 Chrome 打开），通过方向按钮把 X 移动到右下角单元格。
3. [F] BrowserMultiply — 在文件管理器 Downloads 中打开 task.html（用 Chrome 打开），点击按钮 5 次记下显示的数字，把它们的乘积填入表单。
4. [F] SimpleCalendarDeleteEvents — 在日历里按条件删除一组事件。
5. [F] SimpleCalendarDeleteEventsOnRelativeDay — 在日历里删除某个相对日期当天的全部事件。
6. [F] SimpleCalendarDeleteOneEvent — 在日历里删除指定的一个事件。
7. [F] ExpenseAddMultiple — 在 Pro Expense 应用中添加给出的多条支出（通常 3 条）。
8. [F] ExpenseAddMultipleFromGallery — 把相册里发票图片中的支出信息添加到 Pro Expense 应用。
9. [F] ExpenseAddMultipleFromMarkor — 把 Markor 里 expenses.txt 中的支出添加到 Pro Expense 应用。
10. [F] ExpenseDeleteDuplicates — 在 Pro Expense 中删除所有完全重复的支出，每组只保留一条。
11. [F] ExpenseDeleteDuplicates2 — 同上，但噪声条目更多（约 40 条）。
12. [F] ExpenseDeleteMultiple — 在 Pro Expense 中删除给定名字的 3 条支出。
13. [F] ExpenseDeleteMultiple2 — 在 Pro Expense 中删除给定名字的 3 条支出（另有 50 条噪声）。
14. [F] ExpenseDeleteSingle — 在 Pro Expense 中删除给定名字的 1 条支出。
15. [F] RecipeAddMultipleRecipes — 在 Broccoli 食谱应用中添加给出的多份食谱。
16. [F] RecipeAddMultipleRecipesFromImage — 把相册图片里的食谱信息添加到 Broccoli 应用。
17. [F] RecipeAddMultipleRecipesFromMarkor — 把 Markor 里 recipes.txt 中的食谱添加到 Broccoli 应用。
18. [F] RecipeAddMultipleRecipesFromMarkor2 — 把 Markor 里分散的多个食谱笔记添加到 Broccoli 应用。
19. [F] RecipeDeleteDuplicateRecipes — 在 Broccoli 中删除所有完全重复的食谱，每组只保留一条。
20. [F] RecipeDeleteDuplicateRecipes2 — 同上，但噪声数量更大。
21. [F] RecipeDeleteDuplicateRecipes3 — 同上，噪声数量很大且需要滚动才能看到。
22. [F] RecipeDeleteMultipleRecipes — 在 Broccoli 中删除给定名字的 3 份食谱。
23. [F] RecipeDeleteMultipleRecipesWithConstraint — 在 Broccoli 中删除做法里含 {ingredient} 的所有食谱。
24. [F] RecipeDeleteMultipleRecipesWithNoise — 删除指定 3 份食谱（另有 29 条噪声）。
25. [F] RecipeDeleteSingleRecipe — 在 Broccoli 中删除 1 份指定食谱。
26. [F] RecipeDeleteSingleWithRecipeWithNoise — 删除指定 1 份食谱（另有 29 条噪声）。
27. [F] RetroPlaylistDuration — 在 Retro Music 里创建一个总时长符合约束的播放列表。
28. [F] SimpleSmsReply — 用 Simple SMS Messenger 回复指定号码的短信，回复内容给定。
29. [F] SimpleSmsReplyMostRecent — 用 Simple SMS Messenger 回复最近一条收到的短信。
30. [F] SimpleSmsResend — 在 Simple SMS Messenger 里重发上一条发送失败的短信。
31. [F] SimpleSmsSendReceivedAddress — 把最近收到的短信里的地址通过短信转发给另一个号码。
32. [P] MarkorCreateNoteAndSms — 在 Markor 创建指定名字/内容的笔记，然后通过 Simple SMS Messenger 把笔记内容发短信给指定号码。
33. [P] AudioRecorderRecordAudio — 用 Audio Recorder 应用录一段音频并保存。
34. [P] AudioRecorderRecordAudioWithFileName — 用 Audio Recorder 录一段音频，保存时命名为 "{file_name}"。
35. [P] SimpleCalendarAddOneEvent — 在日历添加事件（单个，指定日期时间/标题/描述/地点）。
36. [P] SimpleCalendarAddOneEventInTwoWeeks — 在日历里给两周后的某天添加一个事件。
37. [P] SimpleCalendarAddOneEventRelativeDay — 在日历里给相对某天（例如明天 / 本周五）添加一个事件。
38. [P] SimpleCalendarAddOneEventTomorrow — 在日历里给明天添加一个事件。
39. [P] SimpleCalendarAddRepeatingEvent — 在日历里添加一个周期性重复事件。
40. [P] ExpenseAddSingle — 在 Pro Expense 应用中添加给出的一条支出。
41. [P] FilesDeleteFile — 在 Files 文件管理器中删除指定文件。
42. [P] FilesMoveFile — 在 Files 文件管理器中把指定文件移动到另一个目录。
43. [P] MarkorAddNoteHeader — 在 Markor 的某个笔记顶部添加一段标题/前言。
44. [P] MarkorChangeNoteContent — 修改 Markor 某个笔记的内容。
45. [P] MarkorCreateFolder — 在 Markor 里创建一个名为 {folder_name} 的新文件夹。
46. [P] MarkorCreateNote — 在 Markor 里新建笔记（指定文件名和内容）。
47. [P] MarkorCreateNoteFromClipboard — 把剪贴板内容作为笔记内容，在 Markor 里新建笔记。
48. [P] MarkorDeleteAllNotes — 删除 Markor 中所有的笔记。
49. [P] MarkorDeleteNewestNote — 删除 Markor 中最新的那条笔记。
50. [P] MarkorDeleteNote — 删除 Markor 中名为 {file_name} 的笔记。
51. [P] MarkorEditNote — 编辑 Markor 中的 {file_name}：在顶部/底部加文字 或 替换全文。
52. [P] MarkorMergeNotes — 把 Markor 的多个笔记合并成一个。
53. [P] MarkorMoveNote — 把 Markor 中的某个笔记移动到另一个文件夹。
54. [P] MarkorTranscribeReceipt — 把一张小票图片里的内容在 Markor 中转写成笔记。
55. [P] MarkorTranscribeVideo — 把一段视频里的内容在 Markor 中转写成笔记。
56. [P] OsmAndFavorite — 在 OsmAnd 地图应用中把 {location} 加入收藏。
57. [P] OsmAndMarker — 在 OsmAnd 地图应用中为 {location} 添加一个标记。
58. [P] OsmAndTrack — 在 OsmAnd 中创建一条多点途经的路线/轨迹（Track）。
59. [P] RecipeAddSingleRecipe — 在 Broccoli 食谱应用中添加给出的一份食谱。
60. [P] RetroCreatePlaylist — 在 Retro Music 里创建一个播放列表并加入指定歌曲。
61. [P] RetroPlayingQueue — 在 Retro Music 中把指定歌曲加入当前播放队列。
62. [P] RetroSavePlaylist — 在 Retro Music 里保存/导出一个指定的播放列表。
63. [P] SimpleDrawProCreateDrawing — 在 Simple Draw Pro 里创建一幅画（指定颜色/形状）。
64. [P] SaveCopyOfReceiptTaskEval — 在 Simple Gallery Pro 里把指定小票图片另存一份副本。
65. [P] SimpleSmsSend — 用 Simple SMS Messenger 给指定号码发送指定内容的短信。
66. [P] SimpleSmsSendClipboardContent — 用 Simple SMS Messenger 把剪贴板当前内容发送给指定号码。
67. [P] VlcCreatePlaylist — 在 VLC 里创建一个播放列表并加入指定媒体。
68. [P] VlcCreateTwoPlaylists — 在 VLC 里创建两个不同的播放列表。
69. [Y] TurnOffWifiAndTurnOnBluetooth — 先关闭 WiFi，然后打开蓝牙。
70. [Y] TurnOnWifiAndOpenApp — 先打开 WiFi，然后打开 {app_name} 应用。
71. [Y] CameraTakePhoto — 用相机拍一张照片。
72. [Y] CameraTakeVideo — 用相机录一段视频。
73. [Y] ClockStopWatchPausedVerify — 打开时钟的秒表并确保它处于暂停状态。
74. [Y] ClockStopWatchRunning — 在时钟应用里启动秒表。
75. [Y] ClockTimerEntry — 在时钟里设置一个倒计时（指定时分秒）。
76. [Y] ContactsAddContact — 新建一个联系人 {name}，电话 {number}。
77. [Y] ContactsNewContactDraft — 在通讯录里打开新建联系人页面并填入 {name}/{number}（不保存，只留草稿）。
78. [Y] OpenAppTaskEval — 打开 {app_name} 应用。
79. [Y] SystemBluetoothTurnOff — 把蓝牙关闭。
80. [Y] SystemBluetoothTurnOffVerify — 把蓝牙关闭（设置里确认）。
81. [Y] SystemBluetoothTurnOn — 把蓝牙打开。
82. [Y] SystemBluetoothTurnOnVerify — 把蓝牙打开（设置里确认）。
83. [Y] SystemBrightnessMax — 把屏幕亮度调到最大。
84. [Y] SystemBrightnessMaxVerify — 把屏幕亮度调到最大（设置里确认）。
85. [Y] SystemBrightnessMin — 把屏幕亮度调到最小。
86. [Y] SystemBrightnessMinVerify — 把屏幕亮度调到最小（设置里确认）。
87. [Y] SystemCopyToClipboard — 把以下文本复制到剪贴板：{clipboard_content}。
88. [Y] SystemWifiTurnOff — 关闭 WiFi。
89. [Y] SystemWifiTurnOffVerify — 关闭 WiFi（设置里确认）。
90. [Y] SystemWifiTurnOn — 打开 WiFi。
91. [Y] SystemWifiTurnOnVerify — 打开 WiFi（设置里确认）。

---

## 按「装 app / 断网」分类

### A. 不需要安装新 App（仅用系统自带：相机/时钟/通讯录/系统设置/拨号）

共 23 个：

- **camera**：CameraTakePhoto、CameraTakeVideo
- **clock**：ClockStopWatchPausedVerify、ClockStopWatchRunning、ClockTimerEntry
- **contacts**：ContactsAddContact、ContactsNewContactDraft
- **system 设置**：SystemBluetoothTurnOff(/Verify)、SystemBluetoothTurnOn(/Verify)、SystemBrightnessMax(/Verify)、SystemBrightnessMin(/Verify)、SystemCopyToClipboard、SystemWifiTurnOff(/Verify)、SystemWifiTurnOn(/Verify)
- **条件成立类**（取决于参数指向的 app 是否系统自带）：OpenAppTaskEval、TurnOnWifiAndOpenApp
- **不属于此组**：TurnOffWifiAndTurnOnBluetooth 也只用系统设置，归入 A 组

> 其余 68 个任务都依赖第三方 app（Markor / Simple SMS / Simple Calendar / Simple Gallery / Simple Draw / Audio Recorder / Pro Expense / Broccoli / OsmAnd / Retro Music / VLC / Files (Marc) / Chrome+预置 task.html）。

### B. 执行过程不需要断网（不会主动关 Wi-Fi）

不需要断网的任务：**88 个**（即除去下面 3 个会主动关 Wi-Fi 的）。

会主动关 Wi-Fi 的（B 组排除）：
- TurnOffWifiAndTurnOnBluetooth
- SystemWifiTurnOff
- SystemWifiTurnOffVerify

> 注：开 Wi-Fi、开/关蓝牙、调亮度等不算断网。短信类任务（Simple SMS）在 AndroidWorld 模拟器内是本地行为，不依赖外网。

### A ∩ B：既不用装 app，也不用断网（最容易跑）

共 20 个：

1. CameraTakePhoto
2. CameraTakeVideo
3. ClockStopWatchPausedVerify
4. ClockStopWatchRunning
5. ClockTimerEntry
6. ContactsAddContact
7. ContactsNewContactDraft
8. SystemBluetoothTurnOff
9. SystemBluetoothTurnOffVerify
10. SystemBluetoothTurnOn
11. SystemBluetoothTurnOnVerify
12. SystemBrightnessMax
13. SystemBrightnessMaxVerify
14. SystemBrightnessMin
15. SystemBrightnessMinVerify
16. SystemCopyToClipboard
17. SystemWifiTurnOn
18. SystemWifiTurnOnVerify
19. OpenAppTaskEval（前提：app_name 是系统自带）
20. TurnOnWifiAndOpenApp（前提：app_name 是系统自带）