import React from "react";
import { createRoot } from "react-dom/client";

function HomeWidget() {
  const [count, setCount] = React.useState(0);

  return (
    <div>
      <p>Home counter: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

const root = createRoot(document.getElementById("home-react"));
root.render(<HomeWidget />);
