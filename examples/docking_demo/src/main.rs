use plita::prelude::*;

fn main() -> Result<()> {
    App::new()
        .title("PLITA Docking Demo")
        .window_size(1280, 800)
        .clear_color(ClearColor::rgb(0.105, 0.111, 0.125))
        .continuous_redraw(false)
        .run()
}
