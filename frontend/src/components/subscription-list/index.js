import styles from './styles.module.css'
import cn from 'classnames'
import { Subscription } from '../index'

const SubscriptionList = ({ subscriptions, removeSubscription }) => {
  if(subscriptions) {
   return <div className={styles.subscriptionList}>
      {subscriptions.map(subscription => <Subscription
        key={subscription.id}
        removeSubscription={removeSubscription}
        {...subscription}
      />)}
    </div>
  } else {
    return 'Подписок нет'
  }
  
}

export default SubscriptionList
