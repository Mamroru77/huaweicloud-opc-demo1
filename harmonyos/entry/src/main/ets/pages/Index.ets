@Entry
@Component
struct Index {
  @State message: string = 'Hello World'

  build() {
    RelativeContainer() {
      this.getUI().alignRule({
        center: { anchor: '__container__', align: VerticalAlign.Center },
        middle: { anchor: '__container__', align: HorizontalAlign.Center }
      })
    }
    .height('100%')
    .width('100%')
  }

  getUI() {
    Tabs({ barPosition: BarPosition.Start }) {
      TabContent() {
        this.TabContentOne()
      }
      .tabBar(this.TabOneData)
      .align(Alignment.Top)

      TabContent() {
        this.TabContentTwo()
      }
      .tabBar(this.TabTwoData)

      TabContent() {
        this.TabContentThree()
      }
      .tabBar(this.TabThreeData)
    }
  }

  TabOneData: Resource = $r('app.media.tab_public_icon')
  TabTwoData: Resource = $r('app.media.tab_public_icon')
  TabThreeData: Resource = $r('app.media.tab_public_icon')
  TabFourData: Resource = $r('app.media.tab_public_icon')

  TabContentOne() {
    Column(){
      Text('Hello World').fontSize(50).fontWeight(FontWeight.Bold).fontColor($r('app.color.text'))
      Text($r('app.string.tab')).fontSize(20).fontColor($r('app.color.text')).margin({top: 5})
    }
  }

  TabContentTwo() {
    Column(){
      Text('Hello World 2').fontSize(50).fontWeight(FontWeight.Bold).fontColor($r('app.color.text'))
      Text($r('app.string.tab')).fontSize(20).fontColor($r('app.color.text')).margin({top: 5})
    }
  }

  TabContentThree() {
    Column(){
      Text('Hello World 3').fontSize(50).fontWeight(FontWeight.Bold).fontColor($r('app.color.text'))
      Text($r('app.string.tab')).fontSize(20).fontColor($r('app.color.text')).margin({top: 5})
    }
  }
}
