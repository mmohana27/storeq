export default function Cart({ cart, onUpdate, onRemove }) {
  return (
    <div className="cart" data-testid="cart">
      <h2>Your cart</h2>

      {cart.items.length === 0 ? (
        <div data-testid="cart-empty">Your cart is empty</div>
      ) : (
        <>
          {cart.items.map((i) => (
            <div className="cart-line" key={i.product_id} data-testid="cart-line">
              <span className="cart-name" data-testid="cart-item-name">
                {i.name}
              </span>

              <span className="cart-qty">
                <button
                  data-testid="qty-decrease"
                  onClick={() => onUpdate(i.product_id, i.quantity - 1)}
                >
                  -
                </button>
                <span data-testid="cart-item-qty">{i.quantity}</span>
                <button
                  data-testid="qty-increase"
                  onClick={() => onUpdate(i.product_id, i.quantity + 1)}
                >
                  +
                </button>
              </span>

              <span data-testid="line-total">₹{i.line_total.toFixed(2)}</span>

              <button
                className="danger"
                data-testid="remove-item"
                onClick={() => onRemove(i.product_id)}
              >
                Remove
              </button>
            </div>
          ))}

          <div className="cart-total">
            Total: <span data-testid="cart-total">₹{cart.total.toFixed(2)}</span>
          </div>
        </>
      )}
    </div>
  );
}