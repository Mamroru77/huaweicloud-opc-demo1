@Component
export struct UploadCard {
  build() {
    Column() {
      Row() {
        Image($r('app.media.ic_public_upload')).width(48).height(48)
        Text('上传论文').fontSize(16).fontColor('#007DFF').margin({ left: 8 })
      }.width('100%')
    }
    .width('100%')
    .height(56)
    .backgroundColor('#0A59F7FF')
    .borderRadius(8)
    .alignItems(HorizontalAlign.Center)
    .justifyContent(FlexAlign.Center)
  }
}
