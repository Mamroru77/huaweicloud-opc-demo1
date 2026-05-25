@Component
export struct ProgressPanel {
  build() {
    Column() {
      Column() {
        Progress({ value: 70, total: 100, type: ProgressType.Linear })
          .width(200)
      }
      .width('100%')
      .alignItems(HorizontalAlign.Start)

      Column() {
        Text('析微'.fontSize(12).fontColor('#FFFFFF').opacity(0.9).fontWeight(600))
          .margin({ left: 0, bottom: 0 })

        Text('技术理解'.fontSize(10).fontColor('#FFFFFF').opacity(0.6))
          .margin({ left: 0, top: 1.5, bottom: 0 })

        Text('50%'.fontSize(12).fontColor('#FFFFFF').opacity(0.9).fontWeight(600))
          .margin({ left: 0, top: 8, bottom: 0 })

        Text('提取探针参数中'.fontSize(10).fontColor('#FFFFFF').opacity(0.6))
          .margin({ left: 0, top: 1.5, bottom: 0 })
      }
      .width('100%')
      .alignItems(HorizontalAlign.Start)
      .margin({ top: 12 })
    }
    .width('100%')
    .padding({ top: 20, bottom: 20, left: 16, right: 16 })
    .backgroundColor('#1A0A59F7FF')
    .borderRadius(8)
  }
}
