import React from 'react';
import {
  Subscription,
} from 'react-apollo';
import { Chart } from 'react-google-charts';
import gql from 'graphql-tag';

const GITHUB_STARS_PER_DAY = gql`
subscription {
  github_stars_by_day(order_by: {date: asc}) {
    count
    date
  }
}
`;

const renderChart = (data) => {
  const d = [
    [
      { type: 'date', label: 'Day' },
      'stars'
    ]
  ];
  for (var r of data.github_stars_by_day) {
    d.push([new Date(r.date), parseInt(r.count, 10)]);
  }

  return (
    <Chart className=""
      width={'800px'}
      height={'600px'}
      chartType="LineChart"
      loader={<div>Loading Chart</div>}
      data={d}
      options={{
        hAxis: {
          title: 'Date',
        },
        vAxis: {
          title: 'Stars',
        },
        series: {
          1: { curveType: 'function' },
        },
        height: '100%',
        title: 'Stars per day',
        legend: { position: 'none' },
        animation:{
          duration: 1000,
          easing: 'out',
          startup: true,
        },
      }}
    />
  )
};

export const GitHubStarsPerDay = () => (
  <Subscription subscription={GITHUB_STARS_PER_DAY}>
    {({ loading, error, data }) => {
      if (loading) return <p>Loading...</p>;
      if (error) return <p>Error :</p>;
      return (
        <div>
          <div>
            {renderChart(data)}
          </div>
        </div>
      );
    }}
  </Subscription>
)