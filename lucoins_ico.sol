// Building a Lucoin ICO

pragma solidity ^0.5.2;

contract lucoin_ico {
    
    // Max number of Lucoins available for sale
    uint public max_lucoins = 1000000;
    
    // USD to Lucoins conversion rate
    uint public usd_to_lucoins = 1000;
    
    // Total number of Lucoins bought by investors
    uint public total_lucoins_bought = 0;
    
    // Equity mapped from the investor's address
    mapping(address => uint) equity_lucoins;
    mapping(address => uint) equity_usd;
    
    // Check if an investor can buy Lucoins
    modifier can_buy(uint usd_invested) {
        require (usd_invested * usd_to_lucoins + total_lucoins_bought <= max_lucoins);
        _;
    }
    
    // Get equity in Lucoins
    function get_equity_lucoins(address investor) external view returns (uint) {
        return equity_lucoins[investor];
    }
    
    // Get equity in USD
    function get_equity_usd(address investor) external view returns (uint) {
        return equity_usd[investor];
    }
    
    // Buy Lucoins with USD
    function buy_lucoins(address investor, uint usd_invested) external can_buy(usd_invested) {
        equity_usd[investor] += usd_invested;
        equity_lucoins[investor] += usd_invested * usd_to_lucoins;
        total_lucoins_bought += usd_invested * usd_to_lucoins;
    }
    
    // Sell Lucoins
    function sell_lucoins(address investor, uint lucoins_sold) external {
        equity_usd[investor] -= lucoins_sold / usd_to_lucoins;
        equity_lucoins[investor] -= lucoins_sold;
        total_lucoins_bought -= lucoins_sold;
    }
}