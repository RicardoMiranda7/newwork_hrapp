import {Card as MuiCard, Fade, Slide, Stack} from "@mui/material";
import {styled} from "@mui/material/styles";
import type {ReactNode} from "react";

// Overlay used to ensure the login card is always centered on a clean backdrop.
const Overlay = styled("div")({
  position: "fixed",
  inset: 0,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  width: "100vw",
  minHeight: "100dvh",
  overflow: "hidden",
  zIndex: 1300,
  background: 'linear-gradient(135deg, #f6f9ff 0%, #eef2fb 100%)',
});

// Styled Card with consistent padding, width, and shadow for all auth forms.
const Card = styled(MuiCard)(({theme}) => ({
  display: "flex",
  flexDirection: "column",
  padding: theme.spacing(4),
  gap: theme.spacing(2),
  width: "100%",
  maxWidth: 450,
  boxShadow:
      "hsla(220, 30%, 5%, 0.05) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.05) 0px 15px 35px -5px",
}));

const Center = styled(Stack)({
  alignItems: "center",
  justifyContent: "center",
  width: "100%",
});

interface LogInContainerProps {
  animation?: "fade" | "slide";
  children?: ReactNode;
}

/**
 * A presentational container for authentication screens (e.g., Login, Sign Up).
 * It provides a consistent, centered layout with optional animations.
 * @param animation - The type of entry animation ('slide' or 'fade').
 * @param children - The content to be displayed inside the container.
 */
export default function LogInContainer({
                                         animation = "fade",
                                         children,
                                       }: LogInContainerProps) {
  const content = (
      <Center>
        <Card variant="outlined">{children}</Card>
      </Center>
  );

  return (
      <Overlay>
        {animation === "slide" ? (
            <Slide direction="up" in mountOnEnter unmountOnExit timeout={600}
                   appear>
              {content}
            </Slide>
        ) : (
            <Fade in timeout={600}>{content}</Fade>
        )}
      </Overlay>
  );
}
