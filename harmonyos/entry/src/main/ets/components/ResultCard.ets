@Component
export struct ResultCard {
  build() {
    Column() {
      Column() {
        Row() {
          Column() {
            Text('析微'.fontSize(12).fontColor('#0A59F7FF').fontWeight(600))
              .margin({ left: 0, bottom: 0 })

            Text('技术理解'.fontSize(10).fontColor('#0A59F7FF').opacity(0.6))
              .margin({ left: 0, top: 1.5, bottom: 0 })
          }.alignItems(HorizontalAlign.Start).margin({ right: 0 })

          Row() {
            Text('收起'.fontSize(12).fontColor('#182431').fontWeight(400))
              .margin({ left: 12, top: 2.5, bottom: 2.5 })

            Image($r('app.media.ic_public_arrow_up')).width(16).height(16)
          }
        }.width('100%').justifyContent(FlexAlign.SpaceBetween)

        Column() {
          Row() {
            Text('探针名称'.fontSize(12).fontColor('#66182431').fontWeight(400))
              .margin({ left: 0, bottom: 0 })

            Text('fch'.fontSize(12).fontColor('#182431').fontWeight(600))
              .margin({ left: 24, top: 2.5, bottom: 2.5 })
          }
          .width('100%')
          .alignItems(VerticalAlign.Top)

          Row() {
            Text('探针类型'.fontSize(12).fontColor('#66182431').fontWeight(400))
              .margin({ left: 0, bottom: 0 })

            Text('Activatable probe'.fontSize(12).fontColor('#182431').fontWeight(600))
              .margin({ left: 24, top: 2.5, bottom: 2.5 })
          }
          .width('100%')
          .alignItems(VerticalAlign.Top)
          .margin({ top: 12 })

          Row() {
            Text('临床准备度'.fontSize(12).fontColor('#66182431').fontWeight(400))
              .margin({ left: 0, bottom: 0 })

            Text('TRL 5-6期'.fontSize(12).fontColor('#182431').fontWeight(600))
              .margin({ left: 24, top: 2.5, bottom: 2.5 })
          }
          .width('100%')
          .alignItems(VerticalAlign.Top)
          .margin({ top: 12 })

          Row() {
            Text('查看完整参数'.fontSize(12).fontColor('#007DFF').fontWeight(400))
              .margin({ left: 0, bottom: 0 })

            Image($r('app.media.ic_public_arrow_right')).width(16).height(16)
          }
          .width('100%')
          .alignItems(VerticalAlign.Center)
          .margin({ top: 16 })
        }
        .width('100%')
        .alignItems(HorizontalAlign.Start)
        .margin({ top: 16 })
      }
      .width('100%')
      .alignItems(HorizontalAlign.Start)
    }
    .width('100%')
    .padding({ top: 16, bottom: 16, left: 16, right: 16 })
    .backgroundColor('#FFFFFF')
    .borderRadius(8)
  }
}
