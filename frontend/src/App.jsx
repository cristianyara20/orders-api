import { useState, useEffect } from 'react'
import { IgrDataGrid, IgrTextColumn, IgrNumericColumn } from 'igniteui-react-grids/grids'
import { getOrders } from './services/orderService'

function App() {
  const [orders, setOrders] = useState([])

  useEffect(() => {
    getOrders().then(res => {
      const flat = res.data.map(o => ({
        id: o.id,
        orderNumber: o.orderNumber,
        orderDate: o.orderDate.split('T')[0],
        totalAmount: o.totalAmount,
        cliente: `${o.customer.firstName} ${o.customer.lastName}`,
        ciudad: o.customer.city,
        pais: o.customer.country,
      }))
      setOrders(flat)
    })
  }, [])

  return (
    <div style={{ padding: '20px' }}>
      <h2>Pedidos</h2>
      <IgrDataGrid
        height="500px"
        width="100%"
        dataSource={orders}
        autoGenerateColumns={false}
      >
        <IgrTextColumn field="orderNumber" headerText="# Pedido" width="130" />
        <IgrTextColumn field="orderDate" headerText="Fecha" width="120" />
        <IgrTextColumn field="cliente" headerText="Cliente" width="180" />
        <IgrTextColumn field="ciudad" headerText="Ciudad" width="120" />
        <IgrTextColumn field="pais" headerText="País" width="120" />
        <IgrNumericColumn field="totalAmount" headerText="Total $" width="110" />
      </IgrDataGrid>
    </div>
  )
}

export default App