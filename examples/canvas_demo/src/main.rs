use plita::prelude::*;

fn main() -> Result<()> {
    App::new()
        .title("PLITA Canvas Demo")
        .window_size(1180, 760)
        .clear_color(ClearColor::rgb(0.105, 0.111, 0.125))
        .continuous_redraw(false)
        .run()
}
